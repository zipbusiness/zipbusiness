"""JSON utility functions for the Zip Intelligence API."""

from typing import Any, Dict, List, Union


def flatten_json(data: Union[Dict, List], parent_key: str = '', separator: str = '.') -> Dict[str, Any]:
    """
    Flatten a nested JSON structure into dot notation.
    
    Args:
        data: The JSON data to flatten (dict or list)
        parent_key: The base key for nested fields
        separator: The separator for nested keys (default: '.')
        
    Returns:
        A dictionary with flattened keys in dot notation
    """
    items = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}{separator}{key}" if parent_key else key
            
            if isinstance(value, dict):
                items.extend(flatten_json(value, new_key, separator).items())
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    array_key = f"{new_key}[{i}]"
                    if isinstance(item, (dict, list)):
                        items.extend(flatten_json(item, array_key, separator).items())
                    else:
                        items.append((array_key, item))
            else:
                items.append((new_key, value))
                
    elif isinstance(data, list):
        for i, item in enumerate(data):
            array_key = f"{parent_key}[{i}]" if parent_key else f"[{i}]"
            if isinstance(item, (dict, list)):
                items.extend(flatten_json(item, array_key, separator).items())
            else:
                items.append((array_key, item))
    
    return dict(items)


def get_field_paths(data: Union[Dict, List]) -> List[str]:
    """
    Extract all field paths from a JSON structure.
    
    Args:
        data: The JSON data to analyze
        
    Returns:
        A sorted list of all field paths in dot notation
    """
    flattened = flatten_json(data)
    return sorted(flattened.keys())