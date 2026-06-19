"""Backward-compatible VDT loader shim."""
from app.services.catalog_loader import load_catalog


def load_vdt_codes():
    return load_catalog("vdt").codes
