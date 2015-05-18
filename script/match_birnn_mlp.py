#-*-coding:utf8-*-
import copy, os

from gen_conf_file import *
from dataset_cfg import *

def gen_match_birnn(d_mem, init, lr, dataset):
    # print "ORC: left & right lstm share parameters"
    is_share = False
    net = {}
    # dataset = 'tb_fine'
    # dataset = 'mr'
    if dataset == 'mr':
        net['cross_validation'] = 10

    ds = DatasetCfg(dataset)
    g_filler    = gen_uniform_filter_setting(init)
    zero_filler = gen_zero_filter_setting()
    g_updater   = gen_adagrad_setting(lr = lr, l2 = 0., batch_size = ds.train_batch_size)

    g_layer_setting = {}
    g_layer_setting['no_bias'] = True
    g_layer_setting['w_filler'] = g_filler 
    g_layer_setting['u_filler'] = g_filler
    g_layer_setting['b_filler'] = zero_filler
    g_layer_setting['w_updater'] = g_updater
    g_layer_setting['u_updater'] = g_updater
    g_layer_setting['b_updater'] = g_updater

    net['net_name'] = 'match_bilstm_mlp'
    net['need_reshape'] = False
    net_cfg_train, net_cfg_valid, net_cfg_test = {}, {}, {}
    net['net_config'] = [net_cfg_train, net_cfg_valid, net_cfg_test]
    net_cfg_train["tag"] = "Train"
    net_cfg_train["max_iters"] = ds.train_max_iters 
    net_cfg_train["display_interval"] = ds.train_display_interval
    net_cfg_train["out_nodes"] = ['loss', 'acc']
    net_cfg_valid["tag"] = "Valid"
    net_cfg_valid["max_iters"] = ds.valid_max_iters 
    net_cfg_valid["display_interval"] = ds.valid_display_interval 
    net_cfg_valid["out_nodes"] = ['loss','acc']
    net_cfg_test["tag"] = "Test"
    net_cfg_test["max_iters"]  = ds.test_max_iters 
    net_cfg_test["display_interval"] = ds.test_display_interval
    net_cfg_test["out_nodes"]  = ['loss','acc']
    layers = []
    net['layers'] = layers

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = []
    layer['top_nodes'] = ['x', 'y']
    layer['layer_name'] = 'train_data'
    layer['layer_type'] = 71
    layer['tag'] = ['Train']
    setting = {}
    layer['setting'] = setting
    setting['batch_size'] = ds.train_batch_size
    setting['data_file'] = ds.train_data_file
    setting['max_doc_len'] = ds.max_doc_len
    setting['min_doc_len'] = ds.min_doc_len

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = []
    layer['top_nodes'] = ['x', 'y']
    layer['layer_name'] = 'valid_data'
    layer['layer_type'] = 71
    layer['tag'] = ['Valid']
    setting = {}
    layer['setting'] = setting
    setting['batch_size'] = ds.valid_batch_size
    setting['data_file'] = ds.valid_data_file
    setting['max_doc_len'] = ds.max_doc_len
    setting['min_doc_len'] = ds.min_doc_len

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = []
    layer['top_nodes'] = ['x', 'y']
    layer['layer_name'] = 'test_data'
    layer['layer_type'] = 71
    layer['tag'] = ['Test']
    setting = {}
    layer['setting'] = setting
    setting['batch_size'] = ds.test_batch_size
    setting['data_file'] = ds.test_data_file
    setting['max_doc_len'] = ds.max_doc_len
    setting['min_doc_len'] = ds.min_doc_len

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['x']
    layer['top_nodes'] = ['word_rep_seq']
    layer['layer_name'] = 'embedding'
    layer['layer_type'] = 21
    setting = copy.deepcopy(g_layer_setting)
    layer['setting'] = setting
    setting['embedding_file'] = ds.embedding_file
    setting['update_indication_file'] = ds.update_indication_file
    setting['feat_size'] = ds.d_word_rep
    setting['word_count'] = ds.vocab_size
    setting['w_filler'] = {}
    setting['w_filler']['init_type'] = 2
    setting['w_filler']['range'] = 0.14

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['word_rep_seq']
    layer['top_nodes'] = ['l_lstm_seq']
    layer['layer_name'] = 'l_lstm'
    layer['layer_type'] = 27
    setting = copy.deepcopy(g_layer_setting)
    layer['setting'] = setting
    setting['d_mem'] = d_mem
    setting['reverse'] = False

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['l_lstm_seq']
    layer['top_nodes'] = ['l_pool_rep']
    layer['layer_name'] = 'l_wholePooling'
    layer['layer_type'] =  25 
    setting = {"pool_type":"max"}
    layer['setting'] = setting

    # layer = {}
    # layers.append(layer) 
    # layer['bottom_nodes'] = ['pool_rep']
    # layer['top_nodes'] = ['drop_rep']
    # layer['layer_name'] = 'dropout'
    # layer['layer_type'] =  13
    # setting = {'rate':ds.dp_rate}
    # layer['setting'] = setting

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['word_rep_seq']
    layer['top_nodes'] = ['r_lstm_seq']
    layer['layer_name'] = 'r_lstm'
    layer['layer_type'] = 27
    setting = copy.deepcopy(g_layer_setting)
    layer['setting'] = setting
    setting['d_mem'] = d_mem
    setting['reverse'] = True 
    if is_share:
        print "ORC: share parameters."
        share_setting_w = {}
        share_setting_w['param_id'] = 0
        share_setting_w['source_layer_name'] = 'l_lstm'
        share_setting_w['source_param_id'] = 0
        share_setting_u = {}
        share_setting_u['param_id'] = 1
        share_setting_u['source_layer_name'] = 'l_lstm'
        share_setting_u['source_param_id'] = 1
        share_setting_b = {}
        share_setting_b['param_id'] = 2
        share_setting_b['source_layer_name'] = 'l_lstm'
        share_setting_b['source_param_id'] = 2
        setting['share'] = [share_setting_w, share_setting_u, share_setting_b]

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['r_lstm_seq']
    layer['top_nodes'] = ['r_pool_rep']
    layer['layer_name'] = 'r_wholePooling'
    layer['layer_type'] =  25 
    setting = {"pool_type":"max"}
    layer['setting'] = setting

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['l_pool_rep', 'r_pool_rep']
    layer['top_nodes'] = ['bi_pool_rep']
    layer['layer_name'] = 'concat'
    layer['layer_type'] = 18
    setting = copy.deepcopy(g_layer_setting)
    layer['setting'] = setting
    setting['bottom_node_num'] = 2
    setting['concat_dim_index'] = 3

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['bi_pool_rep']
    layer['top_nodes'] = ['hidden_trans']
    layer['layer_name'] = 'mlp_hidden'
    layer['layer_type'] = 11 
    setting = copy.deepcopy(g_layer_setting)
    layer['setting'] = setting
    setting['num_hidden'] = d_mem * 4

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['hidden_trans']
    layer['top_nodes'] = ['hidden_rep']
    layer['layer_name'] = 'hidden_nonlinear'
    layer['layer_type'] = 1 
    setting = {}
    layer['setting'] = setting
     
    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['hidden_rep']
    layer['top_nodes'] = ['hidden_drop_rep']
    layer['layer_name'] = 'dropout'
    layer['layer_type'] =  13
    setting = {'rate':ds.dp_rate}
    layer['setting'] = setting

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['hidden_drop_rep']
    layer['top_nodes'] = ['softmax_prob']
    layer['layer_name'] = 'softmax_fullconnect'
    layer['layer_type'] = 11 
    setting = copy.deepcopy(g_layer_setting)
    layer['setting'] = setting
    setting['num_hidden'] = ds.num_class
    setting['w_filler'] = zero_filler

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['softmax_prob', 'y']
    layer['top_nodes'] = ['loss']
    layer['layer_name'] = 'softmax_activation'
    layer['layer_type'] = 51 
    setting = {}
    layer['setting'] = setting

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['softmax_prob', 'y']
    layer['top_nodes'] = ['acc']
    layer['layer_name'] = 'accuracy'
    layer['layer_type'] = 56 
    setting = {'topk':1}
    layer['setting'] = setting
    return net

for dataset in ['relation']:
    for d_mem in [50]:
        idx = 0
        for init in [0.2, 0.07]:
            for lr in [0.5, 0.3, 0.1]:
                net = gen_match_birnn(d_mem = d_mem, init = init, lr =lr, dataset=dataset)
                net['log'] = 'log.match.birnn_mlp.max.{0}.d{1}.{2}'.format(dataset, str(d_mem), str(idx))
                # gen_conf_file(net, '/home/wsx/exp/tb/log/run.3/bilstm.max.tb_fine.model.' + str(idx))
                # gen_conf_file(net, '/home/wsx/exp/match/bilstm_mlp/run.4/model.match.bilstm_mlp.last.{0}.d{1}.{2}'.format(dataset, str(d_mem), str(idx)))
                gen_conf_file(net, '/home/wsx/exp/match/birnn_mlp/run.1/model.match.birnn_mlp.max.{0}.d{1}.{2}'.format(dataset, str(d_mem), str(idx)))
                idx += 1
                # os.system("../bin/textnet ../bin/conv_lstm_simulation.model > ../bin/simulation/neg.gen.train.{0}".format(d_mem))
