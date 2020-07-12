#!/usr/bin/env python3

import sys
import argparse
import os
import filecmp
import shutil

###

def exit_if_is_not_folder(path):
	if not os.path.exists(path):
		print('Error: folder', path, 'does not exist!')
		sys.exit(1)
	elif not os.path.isdir(path):
		print('Error:', path, 'is not a folder!')
		sys.exit(1)

def create_if_does_not_exist(path):
	if not os.path.exists(path):
		os.mkdir(path)
		if not os.path.exists(path):
			print('Error: failed to create a folder ' + path + '!')
			sys.exit(1)
	elif not os.path.isdir(path):
		print('Error:', path, 'is not a folder!')
		sys.exit(1)

###

parser = argparse.ArgumentParser(description='Super Map Converter 3k - Global Model Replacement List Generator')

parser.add_argument('-s', '--source', action='store', dest='source_mod_folder', help='Path to the mod for GoldSrc', required=True)
parser.add_argument('-hl', '--half-life', action='store', dest='half_life_folder', help='Path to Half-Life folder', required=True)
parser.add_argument('-o', '--output', action='store', dest='output_folder', help='Path to output folder', required=True)
parser.add_argument('-p', '--prefix', action='store', dest='prefix', type=str, help='Prefix for converted models')
parser.add_argument('-d', '--diff', action='store_true', dest='diff_models', help='Copy only models that are different from Half-Life')
parser.add_argument('-c', '--create-folder', action='store_true', dest='cr_folder', help='Create output folder if it does not exist')
parser.add_argument('-cl', '--classic-mode', action='store_true', dest='cm_override', help='Make overrides for classic mode')
parser.add_argument('-t', '--dry-run', action='store_true', dest='dry', help='Do not modify files')

args = parser.parse_args()

###

mod_path = os.path.relpath(args.source_mod_folder)
exit_if_is_not_folder(mod_path)

hl_path = os.path.relpath(args.half_life_folder)
exit_if_is_not_folder(hl_path)

out_path = os.path.relpath(args.output_folder)
if not args.dry:
	if args.cr_folder:
		create_if_does_not_exist(out_path)
	else:
		exit_if_is_not_folder(out_path)

###

mod_model_path = os.path.join(mod_path, 'models')
exit_if_is_not_folder(mod_model_path)

hl_model_path = os.path.join(hl_path, 'models')
exit_if_is_not_folder(hl_model_path)

out_model_path = os.path.join(out_path, 'models', args.prefix)
create_if_does_not_exist(out_model_path)

###

# PLEASE NOTE: generated file lists are made with non-recursive search!

mod_models = [f for f in os.listdir(mod_model_path) if os.path.isfile(os.path.join(mod_model_path, f))]
hl_models = [f for f in os.listdir(hl_model_path) if os.path.isfile(os.path.join(hl_model_path, f))]

models = []

if args.diff_models:
	for model in mod_models:
		if model in hl_models and not filecmp.cmp(os.path.join(mod_model_path, model), os.path.join(hl_model_path, model)):
			models.append(model)
else:
	models = mod_models

print("Models that are going to be copied:", models)

###

gmr_file = '## Generated with Super Mod Converter 3000\n'

for model in models:
	if not args.dry:
		shutil.copy(os.path.join(mod_model_path, model), out_model_path)
		# trying to find a "texture" model
		model_tex = os.path.join(mod_model_path, model[:-4] + 't.mdl')
		if os.path.exists(model_tex):
			print('Found a texture model for ' + model + '.')
			shutil.copy(model_tex, out_model_path)
	gmr_file += '\"{}\" \"{}\"\n'.format(os.path.join('models', model), os.path.join('models', args.prefix, model))
	if args.cm_override:
		gmr_file += '\"{}\" \"{}\"\n'.format(os.path.join('models', 'hlclassic', model), os.path.join('models', args.prefix, model))

if args.dry:
	print('Your .gmr file:')
	print(gmr_file)
else:
	gmr_path = os.path.join(out_path, 'maps', args.prefix + '.gmr')
	with open(gmr_path, 'w') as f:
		f.write(gmr_file)
	print('Don\'t forget to add "globalmodellist" to you map\'s .cfg file!')

print('Done.')
