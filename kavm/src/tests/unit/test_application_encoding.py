from typing import Any

import pytest

from kavm.adaptors.application import KAVMApplication
from kavm.kavm import KAVM


def application_blank(kavm: KAVM) -> KAVMApplication:
    return KAVMApplication(
        app_id=42, approval_pgm_src=kavm.parse_teal('int 0'), clear_state_pgm_src=kavm.parse_teal('int 1')
    )


@pytest.fixture(params=[application_blank])
def application(kavm: KAVM, request: Any) -> KAVMApplication:
    return request.param(kavm)


def test_application_k_encoding(application: KAVMApplication) -> None:
    rountrip_application = KAVMApplication.from_app_cell(application.app_cell)
    # travers attributes of KAVMAccount and assert that the ones starting with _ are the same,
    # ignoring the __ ones
    for attr in [a for a in dir(application) if a.startswith('_') and not a.startswith('__')]:
        assert getattr(application, attr) == getattr(rountrip_application, attr)


def test_application_to_from_kore(kavm: KAVM, application: KAVMApplication) -> None:
    kore_term = application.to_kore_term(kavm)
    rountrip_application = KAVMApplication.from_kore_term(kore_term, kavm)
    assert rountrip_application == application
