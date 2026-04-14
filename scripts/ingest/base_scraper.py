"""
Base classes for lens data scrapers.
Provides common interface for different data sources.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class LensData:
    """Standardized lens data structure."""
    # Basic info
    brand: str
    model_name: str
    source: str  # dpreview, bhphoto, adorama, manufacturer
    source_url: str

    # Optical specs
    mount: Optional[str] = None
    prime_or_zoom: Optional[str] = None
    focal_length_min: Optional[float] = None
    focal_length_max: Optional[float] = None
    max_aperture_wide: Optional[float] = None
    max_aperture_tele: Optional[float] = None
    min_aperture: Optional[float] = None

    # Features
    sensor_coverage: Optional[str] = None
    autofocus: Optional[bool] = None
    image_stabilization: Optional[bool] = None
    weather_sealing: Optional[bool] = None

    # Physical specs
    min_focus_distance: Optional[float] = None
    max_magnification: Optional[float] = None
    filter_thread: Optional[float] = None
    weight: Optional[float] = None
    diameter: Optional[float] = None
    length: Optional[float] = None

    # Pricing
    msrp: Optional[float] = None
    current_price: Optional[float] = None
    currency: Optional[str] = "USD"

    # Dates
    release_date: Optional[str] = None
    discontinued_date: Optional[str] = None
    fetched_at: Optional[str] = None

    # Additional
    raw_title: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'brand': self.brand,
            'model_name': self.model_name,
            'source': self.source,
            'source_url': self.source_url,
            'mount': self.mount,
            'prime_or_zoom': self.prime_or_zoom,
            'focal_length_min': self.focal_length_min,
            'focal_length_max': self.focal_length_max,
            'max_aperture_wide': self.max_aperture_wide,
            'max_aperture_tele': self.max_aperture_tele,
            'min_aperture': self.min_aperture,
            'sensor_coverage': self.sensor_coverage,
            'autofocus': self.autofocus,
            'image_stabilization': self.image_stabilization,
            'weather_sealing': self.weather_sealing,
            'min_focus_distance': self.min_focus_distance,
            'max_magnification': self.max_magnification,
            'filter_thread': self.filter_thread,
            'weight': self.weight,
            'diameter': self.diameter,
            'length': self.length,
            'msrp': self.msrp,
            'current_price': self.current_price,
            'currency': self.currency,
            'release_date': self.release_date,
            'discontinued_date': self.discontinued_date,
            'fetched_at': self.fetched_at,
            'raw_title': self.raw_title,
        }


class BaseScraper(ABC):
    """Base class for all lens scrapers."""

    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    def discover_lenses(self, brand: str, limit: int = 20) -> list[dict]:
        """
        Discover lens product pages for a brand.

        Returns:
            List of dicts with keys: brand, title, url
        """
        pass

    @abstractmethod
    def fetch_page(self, url: str) -> str:
        """
        Fetch a single page's HTML content.

        Returns:
            HTML content as string
        """
        pass

    @abstractmethod
    def parse_lens_detail(self, html: str) -> LensData:
        """
        Parse lens details from HTML.

        Returns:
            LensData object
        """
        pass

    def scrape_lens(self, url: str, title: str, brand: str) -> LensData:
        """
        Complete scraping workflow for a single lens.
        """
        html = self.fetch_page(url)
        lens_data = self.parse_lens_detail(html)

        # Fill in metadata
        lens_data.source = self.source_name
        lens_data.source_url = url
        lens_data.raw_title = title
        lens_data.brand = brand
        lens_data.fetched_at = datetime.utcnow().isoformat() + 'Z'

        return lens_data

    def scrape_brand(self, brand: str, limit: int = 20) -> list[LensData]:
        """
        Scrape multiple lenses for a brand.
        """
        discovered = self.discover_lenses(brand, limit)
        results = []

        for item in discovered:
            try:
                lens_data = self.scrape_lens(
                    url=item['url'],
                    title=item['title'],
                    brand=item['brand']
                )
                results.append(lens_data)
            except Exception as e:
                print(f"Error scraping {item['url']}: {e}")
                continue

        return results
