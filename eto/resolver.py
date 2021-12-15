from typing import Iterable

from rikai.io import _normalize_uri
from rikai.parquet.resolver import DefaultResolver, Resolver

import eto


class EtoDatasetResolver(DefaultResolver):
    """
    Custom rikai resolver for datasets in the Eto dataset registry
    """

    def resolve(self, dataset_name: str) -> Iterable[str]:
        dataset = eto.get_dataset(dataset_name)
        return super().resolve(_normalize_uri(dataset.uri))


def register_resolver():
    """To be called at singleton sdk client initialization"""
    eto_resolver = EtoDatasetResolver()
    Resolver.set_default_scheme("eto")
    Resolver.register("eto", eto_resolver)
