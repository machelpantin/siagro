from pathlib import Path
import pandas as pd
import logging
from datetime import datetime


# -------------------------
# Logger setup (safe default)
# -------------------------
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

# -------------------------
# Base directory utilities
# -------------------------
def get_base_dir() -> Path:
    """Return the directory of this script if available, otherwise the current working directory."""
    try:
        return Path(__file__).resolve().parent
    except NameError:
        return Path.cwd()

# -------------------------
# Directory setup
# -------------------------
def get_paths(module: str = "default_module", year: str | None = None):
    """
    Create and return base, output, and cache directories.

    Args:
        module: Name of the module or dataset group (e.g. "secmca")
        year: Optional year folder (defaults to current year)

    Returns:
        dict with 'base', 'output', and 'cache' Path objects
    """
    base_dir = get_base_dir()
    year_folder = year or str(datetime.now().year)

    output_dir = base_dir / "outputs" / "siagro_uploads" / year_folder / module
    cache_dir = base_dir / "cache" / module

    # Ensure folders exist
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Cache directory:  {cache_dir}")

    return {
        "base": base_dir,
        "output": output_dir,
        "cache": cache_dir,
    }

# -------------------------
# Optional convenience exports
# -------------------------
# Example usage
#_paths = get_paths("secmca")
#BASE_DIR = _paths["base"]
#OUTPUT_DIR = _paths["output"]
#CACHE_DIR = _paths["cache"]


# =========================
# Download dimension data
# =========================
def load_dimension_data(indicator_id, lang="en", cache_dim=True):
    """
    Load dimension data from CEPALSTAT API or local cache.

    Parameters:
    - indicator_id: int, CEPALSTAT indicator ID.
    - lang: str, language code ('en', 'es').
    - cache_dim: bool, whether to use local cached dimension data if available.

    Returns:
    - pandas DataFrame with dimension data, or None if loading fails.
    """
    # Check if dim data is cached
    cache_path = get_base_dir() / "cache" / f'cache_dim_{indicator_id}.pkl'
    if cache_dim and cache_path.exists():
        dim = pd.read_pickle(cache_path)
        logging.info(f"Loaded cached dimension data for indicator {indicator_id}.")
    else:
        try:
            dim_url = f'https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/{indicator_id}/dimensions?lang={lang}&format=excel&in=1'
            dim = pd.read_excel(dim_url)
            if cache_dim:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                dim.to_pickle(cache_path)
            logging.info(f"Loaded dimension data for indicator {indicator_id} from CEPALSTAT API.")
        except Exception as e:
            logging.error(f"Failed to load dimension data for indicator {indicator_id}: {e}")
            return None
    return dim

# =========================
# Download cepalstat data
# =========================
def cepal_data(indicator_ids, lang='en', start_year=None, end_year=None, countries=None, save_csv=False, csv_filename='cepalstat_indicators.csv'):
    """
    Fetch data for multiple indicators from CEPALSTAT API,
    convert dimension IDs to human-readable names, and combine into a single DataFrame.
    Optionally filter results by year range and country ISO codes.

    This version preserves the original dim_* columns and adds new "<dimension_name>"
    columns containing the human-readable member names.
    """
    import requests
    # Create an empty list to store individual DataFrames
    dfs = []

    # Loop through each indicator ID
    for indicator_id in indicator_ids:
        logger.info(f"Fetching data for indicator {indicator_id}...")

        # 1. Fetch the data
        data_url = f"https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/{indicator_id}/data"
        data_params = {'lang': lang, 'format': 'json'}
        response = requests.get(data_url, params=data_params)

        if response.status_code != 200:
            logger.error(f"Error fetching data for indicator {indicator_id}: {response.status_code}")
            continue

        data = response.json()

        # Check if there's data
        if not data['body']['data']:
            logger.info(f"No data available for indicator {indicator_id}")
            continue

        df = pd.DataFrame(data['body']['data'])

        # Add indicator ID as a column
        df['indicator_id'] = indicator_id

        # 2. Fetch the dimensions information
        dimensions_url = f"https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/{indicator_id}/dimensions"
        dimensions_params = {'lang': lang, 'format': 'json', 'in': 1, 'path': 0}
        dimensions_response = requests.get(dimensions_url, params=dimensions_params)

        if dimensions_response.status_code != 200:
            logger.error(f"Error fetching dimensions for indicator {indicator_id}: {dimensions_response.status_code}")
            dfs.append(df)  # Add data without transformations
            continue

        dimensions_data = dimensions_response.json()

        # 3. Create mappings for dimensions and their members
        dimension_name_map = {}  # Maps dimension column names (dim_XXX) to proper names
        dimension_member_maps = {}  # Maps member IDs to member names for each dimension

        for dimension in dimensions_data['body']['dimensions']:
            dim_id = dimension['id']
            dim_column = f"dim_{dim_id}"
            dim_name = dimension['name']

            # Store column name mapping
            dimension_name_map[dim_column] = dim_name

            # Create member mapping for this dimension
            member_map = {}
            for member in dimension['members']:
                member_map[member['id']] = member['name']

            # Store member mapping
            dimension_member_maps[dim_column] = member_map

        # 4. Fetch metadata to get the indicator name
        metadata_url = f"https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/{indicator_id}/metadata"
        metadata_params = {'lang': lang, 'format': 'json'}
        metadata_response = requests.get(metadata_url, params=metadata_params)

        indicator_name = f"Indicator {indicator_id}"
        if metadata_response.status_code == 200:
            metadata = metadata_response.json()

            # Based on the actual API structure, the indicator name is in metadata['body']['metadata']['indicator_name']
            if 'body' in metadata and 'metadata' in metadata['body'] and 'indicator_name' in metadata['body']['metadata']:
                indicator_name = metadata['body']['metadata']['indicator_name']

            # Fallbacks for any structure changes
            elif 'body' in metadata:
                if 'indicator_name' in metadata['body']:
                    indicator_name = metadata['body']['indicator_name']
                elif 'indicators' in metadata['body'] and metadata['body']['indicators']:
                    indicator_name = metadata['body']['indicators'][0].get('name', indicator_name)
                elif 'name' in metadata['body']:
                    indicator_name = metadata['body']['name']
                elif 'title' in metadata['body']:
                    indicator_name = metadata['body']['title']

        # Add indicator name column
        df['indicator_name'] = indicator_name

        # 5. Preserve original dim_* columns and add new "<dimension_name>" columns
        for dim_col, member_map in dimension_member_maps.items():
            if dim_col in df.columns:
                # Label column uses the human-readable dimension name if available, otherwise falls back to dim_col
                label_col = f"{dimension_name_map.get(dim_col, dim_col)}"
                # Normalize mapping keys to strings so mapping works regardless of numeric/string types
                member_map_str = {str(k): v for k, v in member_map.items()}
                df[label_col] = df[dim_col].astype(str).map(member_map_str)

        # Add the processed DataFrame to our list
        dfs.append(df)
        logger.info(f"Successfully processed indicator {indicator_id}, {len(df)} rows")

    # Combine all DataFrames into one
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)

        # Filter by year range if specified
        if start_year is not None or end_year is not None:
            # Check for the specific year columns used by CEPALSTAT
            year_column = None
            if 'Años__ESTANDAR' in combined_df.columns:
                year_column = 'Años__ESTANDAR'
            elif 'Years__ESTANDAR' in combined_df.columns:
                year_column = 'Years__ESTANDAR'

            # If neither of the specific columns was found, try to find any other year column
            if year_column is None:
                potential_year_columns = ['Year', 'TIME', 'Time', 'YEAR', 'year', 'Period', 'period', 'TIME_PERIOD']

                for col in potential_year_columns:
                    if col in combined_df.columns:
                        year_column = col
                        break

                # If still no year column found, try to find columns with 'year' in the name
                if year_column is None:
                    for col in combined_df.columns:
                        if 'year' in col.lower() or 'año' in col.lower():
                            year_column = col
                            break

            # If a year column was found, filter by it
            if year_column:
                # Convert year to numeric for proper comparison
                combined_df[year_column] = pd.to_numeric(combined_df[year_column], errors='coerce')

                # Apply filters
                if start_year is not None:
                    combined_df = combined_df[combined_df[year_column] >= start_year]
                if end_year is not None:
                    combined_df = combined_df[combined_df[year_column] <= end_year]

                logger.info(f"Filtered data to years: {start_year or 'earliest'} to {end_year or 'latest'} using column '{year_column}'")
            else:
                logger.warning("Warning: Could not identify a year column for filtering")

        # Filter by country ISO codes if specified
        if countries and len(countries) > 0:
            # Check for the ISO column
            if 'iso3' in combined_df.columns:
                # Convert all country codes to uppercase for consistent comparison
                combined_df['iso3'] = combined_df['iso3'].str.upper() if combined_df['iso3'].dtype == 'object' else combined_df['iso3']
                country_list_upper = [c.upper() for c in countries]

                # Filter the DataFrame to include only the specified countries
                original_len = len(combined_df)
                combined_df = combined_df[combined_df['iso3'].isin(country_list_upper)]
                filtered_len = len(combined_df)

                logger.info(f"Filtered data to {len(countries)} countries: {', '.join(countries)}")
                logger.info(f"Rows before country filtering: {original_len}, after: {filtered_len}")

                # Check if any country codes didn't return data
                found_countries = combined_df['iso3'].unique()
                missing_countries = [c for c in country_list_upper if c not in found_countries]
                if missing_countries:
                    logger.warning(f"Warning: No data found for these countries: {', '.join(missing_countries)}")
            else:
                logger.warning("Warning: Could not find 'iso3' column for country filtering")

        logger.info(f"Final combined DataFrame has {len(combined_df)} rows")

        # Save to CSV if requested
        if save_csv:
            combined_df.to_csv(csv_filename, index=False)
            logger.info(f"Data saved to '{csv_filename}'")

        return combined_df
    else:
        logger.info("No data was retrieved for any of the indicators")
        return None

# Example usage:
# indicator_data = fetch_data_detailed(
#     [2778, 2806], 
#     start_year=2015, 
#     end_year=2020, 
#     countries=['BRA', 'MEX', 'ARG'],
#     save_csv=True
# )