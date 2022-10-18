import json
import tempfile
from base64 import b64decode, b64encode
from pathlib import Path
from typing import Any, Dict, cast

from pyk.kast import KApply, KAst, KInner, KSort, KToken
from pyk.kastManip import split_config_from
from pyk.prelude import intToken

from kavm.pyk_utils import tvalue


class KAVMApplication:
    """
    Convenience class abstracting an Algorand smart contract (aka stateful application)
    """

    def __init__(
        self,
        app_id: int,
        approval_pgm_src: KAst,
        clear_state_pgm_src: KAst,
        approval_pgm: bytes = b'',
        clear_state_pgm: bytes = b'',
        global_ints: int = 0,
        global_bytes: int = 0,
        global_int_data: Dict = {},
        global_bytes_data: Dict = {},
        local_ints: int = 0,
        local_bytes: int = 0,
        extra_pages: int = 0,
    ) -> None:
        """
        Create a KAVM app cell.
        """
        self._app_id = app_id
        self._approval_pgm_src = approval_pgm_src
        self._clear_state_pgm_src = clear_state_pgm_src
        self._approval_pgm = approval_pgm
        self._clear_state_pgm = clear_state_pgm
        self._global_ints = global_ints
        self._global_bytes = global_bytes
        self._global_int_data = global_int_data
        self._global_bytes_data = global_bytes_data
        self._local_ints = local_ints
        self._local_bytes = local_bytes
        self._extra_pages = extra_pages

    # TODO: implement better eq
    def __eq__(self, other: Any) -> bool:
        return self._app_id == other._app_id

    @property
    def address(self) -> str:
        raise NotImplementedError()

    @property
    def app_cell(self) -> KInner:

        def from_list_bytes(d):
            if len(d) == 0:
                return KApply('.Map')
            if len(d) == 1:
                return KApply('_|->_', args=[KToken(token='b\"' + d[0][0] + '\"', sort=KSort(name='Bytes')),
                    KToken(token='b\"' + d[0][1][2:-1] + '\"', sort=KSort(name='Bytes'))])
            return KApply('_Map_', [from_list_bytes(d[0:1]), from_list_bytes(d[1:])])

        def from_list_ints(d):
            if len(d) == 0:
                return KApply('.Map')
            if len(d) == 1:
                return KApply('_|->_', args=[KToken(token='b\"' + d[0][0] + '\"', sort=KSort(name='Bytes')),
                    KToken(token=str(d[0][1]), sort=KSort(name='Int'))])
            return KApply('_Map_', [from_list_ints(d[0:1]), from_list_ints(d[1:])])

        return KApply(
            '<app>',
            [
                KApply('<appID>', [intToken(self._app_id)]),
                KApply('<approvalPgmSrc>', cast(KInner, self._approval_pgm_src)),
                KApply('<clearStatePgmSrc>', cast(KInner, self._clear_state_pgm_src)),
                KApply('<approvalPgm>', tvalue(self._approval_pgm)),
                KApply('<clearStatePgm>', tvalue(self._clear_state_pgm)),
                KApply(
                    '<globalState>',
                    [
                        KApply('<globalNumInts>', [intToken(self._global_ints)]),
                        KApply('<globalNumBytes>', [intToken(self._global_bytes)]),
                        # NOTE: these two cells MUST BE in the same order as they are declared in the K configuration
                        KApply('<globalBytes>', from_list_bytes([(k,str(b64decode(v))) for k,v in self._global_bytes_data.items()])),
                        KApply('<globalInts>', from_list_ints([(k,v) for k,v in self._global_int_data.items()])),
                    ],
                ),
                KApply(
                    '<localState>',
                    [
                        KApply('<localNumInts>', [intToken(self._local_ints)]),
                        KApply('<localNumBytes>', [intToken(self._local_bytes)]),
                    ],
                ),
                KApply('<extraPages>', [intToken(self._extra_pages)]),
            ],
        )
        return test

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
        def from_map(term: KInner) -> Dict:
            if term.label.name == '_|->_':
                if term.args[1].sort.name == 'Bytes':
                    return {term.args[0].token[2:-1]: b64encode(bytes(term.args[1].token[2:-1], encoding="raw_unicode_escape"))}
                if term.args[1].sort.name == 'Int':
                    return {term.args[0].token[2:-1]: int(term.args[1].token)}
            if term.label.name == '_Map_':
                return from_map(term.args[0]) | from_map(term.args[1])
            if term.label.name == '.Map':
                return {}
        """
        Parse a KAVMApplication instance from a Kast term
        """
        (_, subst) = split_config_from(term)
        print("from_app_cell")
        print(subst['GLOBALBYTES_CELL'])
        return KAVMApplication(
            app_id=int(subst['APPID_CELL'].token),
            approval_pgm_src=subst['APPROVALPGMSRC_CELL'],
            clear_state_pgm_src=subst['CLEARSTATEPGMSRC_CELL'],
            approval_pgm=b64decode(subst['APPROVALPGM_CELL'].token),
            clear_state_pgm=b64decode(subst['CLEARSTATEPGM_CELL'].token),
            global_ints=int(subst['GLOBALNUMINTS_CELL'].token),
            global_bytes=int(subst['GLOBALNUMBYTES_CELL'].token),
            global_int_data=from_map(subst['GLOBALINTS_CELL']),
            global_bytes_data=from_map(subst['GLOBALBYTES_CELL']),
            local_ints=int(subst['LOCALNUMINTS_CELL'].token),
            local_bytes=int(subst['LOCALNUMBYTES_CELL'].token),
            extra_pages=int(subst['EXTRAPAGES_CELL'].token),
        )

    def dictify(self) -> Dict[str, Any]:
        """
        Return a dictified representation of the application cell to pass to py-algorand-sdk
        """
        print("dictify")
        print(self._global_bytes_data)
        return {
            'index': str(self._app_id),
            'params': {
                'creator': '',
                'approval-progam': self._approval_pgm,
                'clear-state-program': self._clear_state_pgm,
                'extra-program-pages': self._extra_pages,
                'local-state-schema': {},
                'global-state-schema': {},
                'global-state': 
                    [{'key': b64encode(k.encode('ascii')), 'value':{'bytes':v}} for k,v in self._global_bytes_data.items()]
                    +   [{'key': b64encode(k.encode('ascii')), 'value':{'uint':v}} for k,v in self._global_int_data.items()]
            },
        }
