import importlib.util as _u, pathlib as _p
_s=_u.spec_from_file_location("cfg", _p.Path(__file__).with_name("00_config.py"))
cfg=_u.module_from_spec(_s); _s.loader.exec_module(cfg)
globals().update({k:v for k,v in vars(cfg).items() if not k.startswith("_")})
