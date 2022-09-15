from base64 import b64decode
from typing import Dict, List, Optional, Union, cast, Any
import tempfile
import json
from pathlib import Path

from pyk.kast import KApply, KInner, KSort, KToken, Subst, KLabel, KAst
from pyk.kastManip import flatten_label, split_config_from
from pyk.prelude import intToken

from kavm.constants import MIN_BALANCE
from kavm.pyk_utils import tvalue


class KAVMApplication:
    """
    Convenience class abstracting an Algorand smart contract (aka stateful application)
    """

    def __init__(
        self,
        appID: int,
        approvalPgmSrc: KAst,
        clearStatePgmSrc: KAst,
        approvalPgm: bytes = b'',
        clearStatePgm: bytes = b'',
        globalInts: int = 0,
        globalBytes: int = 0,
        localInts: int = 0,
        localBytes: int = 0,
        extraPages: int = 0,
    ) -> None:
        """
        Create a KAVM app cell.
        """
        self._appID = appID
        self._approvalPgmSrc = approvalPgmSrc
        self._clearStatePgmSrc = clearStatePgmSrc
        self._approvalPgm = approvalPgm
        self._clearStatePgm = clearStatePgm
        self._globalInts = globalInts
        self._globalBytes = globalBytes
        self._localInts = localInts
        self._localBytes = localBytes
        self._extraPages = extraPages

    # TODO: implement better eq
    def __eq__(self, other: 'KAVMApplication') -> bool:
        return self._appID == other._appID

    @property
    def address(self) -> str:
        raise NotImplemented()

    @property
    def app_cell(self) -> KInner:
        return KApply(
            '<app>',
            [
                KApply('<appID>', [intToken(self._appID)]),
                KApply('<approvalPgmSrc>', cast(KInner, self._approvalPgmSrc)),
                KApply('<clearStatePgmSrc>', cast(KInner, self._clearStatePgmSrc)),
                KApply('<approvalPgm>', tvalue(self._approvalPgm)),
                KApply('<clearStatePgm>', tvalue(self._clearStatePgm)),
                KApply(
                    '<globalState>',
                    [
                        KApply('<globalInts>', [intToken(self._globalInts)]),
                        KApply('<globalBytes>', [intToken(self._globalBytes)]),
                        KApply('<globalStorage>', [KApply('.Map')]),
                    ],
                ),
                KApply(
                    '<localState>',
                    [
                        KApply('<localInts>', [intToken(self._localInts)]),
                        KApply('<localBytes>', [intToken(self._localBytes)]),
                    ],
                ),
                KApply('<extraPages>', [intToken(self._extraPages)]),
            ],
        )

    def to_kore_term(self, kavm: Any) -> str:
        '''
        Encode application as a KORE term

        A KAVM instance must be passed to use kavm.kast
        '''
        with tempfile.NamedTemporaryFile('w+t', delete=True) as tmp_kast_json_file:
            term = self.app_cell
            term_json = json.dumps({'format': 'KAST', 'version': 2, 'term': term.to_dict()})
            tmp_kast_json_file.write(term_json)
            tmp_kast_json_file.seek(0)
            kore_term = kavm.kast(
                input_file=Path(tmp_kast_json_file.name),
                module='APPLICATIONS',
                sort=KSort('AppCell'),
                input='json',
                output='kore',
            ).stdout
            return kore_term

    @staticmethod
    def from_kore_term(kore_term: str, kavm: Any) -> 'KAVMApplication':
        '''
        Decode an application from a KORE term

        A KAVM instance must be passed to use kavm.kast
        '''
        with tempfile.NamedTemporaryFile('w+t', delete=True) as tmp_kore_file:
            tmp_kore_file.write(kore_term)
            tmp_kore_file.seek(0)
            kast_term_json = kavm.kast(
                input_file=Path(tmp_kore_file.name),
                module='APPLICATIONS',
                sort=KSort('AppCell'),
                input='kore',
                output='json',
            ).stdout
            kast_term = KAst.from_dict(json.loads(kast_term_json)['term'])
            return KAVMApplication.from_app_cell(cast(KInner, kast_term))

    @staticmethod
    def to_app_cell(app: 'KAVMApplication') -> KInner:
        return app.app_cell

    @staticmethod
    def from_app_cell(term: KInner) -> 'KAVMApplication':
        """
        Parse a KAVMApplication instance from a Kast term
        """
        (_, subst) = split_config_from(term)
        return KAVMApplication(
            appID=int(subst['APPID_CELL'].token),
            approvalPgmSrc=subst['APPROVALPGMSRC_CELL'],
            clearStatePgmSrc=subst['CLEARSTATEPGMSRC_CELL'],
            approvalPgm=b64decode(subst['APPROVALPGM_CELL'].token),
            clearStatePgm=b64decode(subst['CLEARSTATEPGM_CELL'].token),
            globalInts=int(subst['GLOBALINTS_CELL'].token),
            globalBytes=int(subst['GLOBALBYTES_CELL'].token),
            localInts=int(subst['LOCALINTS_CELL'].token),
            localBytes=int(subst['LOCALBYTES_CELL'].token),
            extraPages=int(subst['EXTRAPAGES_CELL'].token),
        )

    def dictify(self) -> Dict[str, Union[str, int]]:
        """
        Return a dictified representation of the application cell to pass to py-algorand-sdk
        """
        return {
            'index': str(self._appID),
        }
