import argparse
import os
import subprocess
import torch
import numpy as np
from utils.numba_utils import numba_manual_seed
import time
import yaml

global_print_hparams = True
hparams = {}


class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)


def override_config(old_config: dict, new_config: dict):
    for k, v in new_config.items():
        if isinstance(v, dict) and k in old_config:
            override_config(old_config[k], new_config[k])
        else:
            old_config[k] = v


def set_hparams(config='', exp_name='', hparams_str='', print_hparams=True, global_hparams=True):
    if config == '' and exp_name == '':
        parser = argparse.ArgumentParser(description='')
        parser.add_argument('--config', type=str, default='configs/scenarios/continuous_uav_mbs/sdrgn.yaml',
                            help='location of the data corpus')
        parser.add_argument('--exp_name', type=str, default='uav-mbs_sdrgn', help='exp_name')
        parser.add_argument('--hparams', type=str, default='',
                            help='location of the data corpus')
        parser.add_argument('--display', action='store_true', help='display')
        parser.add_argument('--evaluate', action='store_true', help='evaluate')
        parser.add_argument('--reset', default=True, action='store_true', help='reset_config')
        parser.add_argument('--remove', action='store_true', help='reset_config')
        parser.add_argument('--seed', type=int, default=int(time.time()))
        args, unknown = parser.parse_known_args()

    else:
        args = Args(config=config, exp_name=exp_name, hparams=hparams_str,
                    infer=False, validate=False, reset=False, debug=False)
    global hparams
    assert args.config != '' or args.exp_name != ''

    config_chains = []
    loaded_config = set()

    def load_config(config_fn):  # deep first
        if not os.path.exists(config_fn):
            return {}
        with open(config_fn) as f:
            hparams_ = yaml.safe_load(f)
        loaded_config.add(config_fn)
        if 'base_config' in hparams_:
            ret_hparams = {}
            if not isinstance(hparams_['base_config'], list):
                hparams_['base_config'] = [hparams_['base_config']]
            for c in hparams_['base_config']:
                if c.startswith('.'):
                    c = f'{os.path.dirname(config_fn)}/{c}'
                    c = os.path.normpath(c)
                if c not in loaded_config:
                    override_config(ret_hparams, load_config(c))
            override_config(ret_hparams, hparams_)
        else:
            ret_hparams = hparams_
        config_chains.append(config_fn)
        return ret_hparams

    saved_hparams = {}
    args_work_dir = ''
    if args.exp_name != '':
        args_work_dir = f'checkpoints/{args.exp_name}'
        ckpt_config_path = f'{args_work_dir}/config.yaml'
        if os.path.exists(ckpt_config_path):
            with open(ckpt_config_path) as f:
                saved_hparams.update(yaml.safe_load(f))
    hparams_ = {}
    if args.config != '':
        hparams_.update(load_config(args.config))
    if not args.reset:
        hparams_.update(saved_hparams)
    hparams_['work_dir'] = args_work_dir

    # --hparams="a=1,b.c=2,d=[1 1 1]"
    if args.hparams != "":
        for new_hparam in args.hparams.split(","):
            k, v = new_hparam.split("=")
            v = v.strip("\'\" ")
            config_node = hparams_
            for k_ in k.split(".")[:-1]:
                config_node = config_node[k_]
            k = k.split(".")[-1]
            if v in ['True', 'False'] or type(config_node[k]) in [bool, list, dict]:
                if type(config_node[k]) == list:
                    v = v.replace(" ", ",")
                config_node[k] = eval(v)
            else:
                config_node[k] = type(config_node[k])(v)
    if args_work_dir != '' and args.remove:
        answer = input("REMOVE old checkpoint? Y/N [Default: N]: ")
        if answer.lower() == "y":
            subprocess.check_call(f'rm -rf {args_work_dir}', shell=True)
    if args_work_dir != '' and (not os.path.exists(ckpt_config_path) or args.reset):
        os.makedirs(hparams_['work_dir'], exist_ok=True)
        with open(ckpt_config_path, 'w') as f:
            yaml.safe_dump(hparams_, f)

    hparams_['exp_name'] = args.exp_name
    hparams_['display'] = args.display
    hparams_['evaluate'] = args.evaluate
    hparams_['seed'] = args.seed
    
    # 进行数据增强的列表（0表示水平镜面对称，1表示垂直镜面对称，2表示顺时针90°，3表示顺时针180°，4表示顺时针270°）
    hparams_['data_trans_list'] = [2]
    # 记录地图大小
    hparams["world_size"] = []
    
    global global_print_hparams
    if global_hparams:
        hparams.clear()
        hparams.update(hparams_)
    if print_hparams and global_print_hparams and global_hparams:
        print('| Hparams chains: ', config_chains)
        print('| Hparams: ')
        for i, (k, v) in enumerate(sorted(hparams_.items())):
            print(f"\033[;33;m{k}\033[0m: {v}, ", end="\n" if i % 5 == 4 else "")
        print("")
        global_print_hparams = False

    torch.manual_seed(hparams_['seed'])
    torch.cuda.manual_seed(hparams_['seed'])
    np.random.seed(hparams_['seed'])
    numba_manual_seed(hparams_['seed'])
    return hparams_