#!/usr/bin/env python3

import sys
import argparse
import os
import filecmp
import shutil
import ntpath

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

def recursive_search(path):
	temp_list = []
	for dir_, _, files in os.walk(path):
		for fn in files:
			rel_dir = os.path.relpath(dir_, path)
			rel_file = os.path.join(rel_dir, fn)
			temp_list.append(rel_file)
	return temp_list

###

parser = argparse.ArgumentParser(description='Super Map Converter 3k - Global Sound Replacement List Generator')

parser.add_argument('-s', '--source', action='store', dest='source_mod_folder', help='Path to the mod for GoldSrc', required=True)
parser.add_argument('-hl', '--half-life', action='store', dest='half_life_folder', help='Path to Half-Life folder', required=True)
parser.add_argument('-o', '--output', action='store', dest='output_folder', help='Path to output folder', required=True)
parser.add_argument('-p', '--prefix', action='store', dest='prefix', type=str, help='Prefix for converted sounds')
parser.add_argument('-d', '--diff', action='store_true', dest='diff_sounds', help='Copy only sounds that are different from Half-Life')
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

mod_sound_path = os.path.join(mod_path, 'sound')
exit_if_is_not_folder(mod_sound_path)

hl_sound_path = os.path.join(hl_path, 'sound')
exit_if_is_not_folder(hl_sound_path)

out_sound_path = os.path.join(out_path, 'sound', args.prefix)
create_if_does_not_exist(out_sound_path)

###

# PLEASE NOTE: only sound file list is generated with recursive search!

mod_sounds = recursive_search(mod_sound_path)
hl_sounds = recursive_search(hl_sound_path)

sounds = []

if args.diff_sounds:
	for sound in mod_sounds:
		if sound in hl_sounds and not filecmp.cmp(os.path.join(mod_sound_path, sound), os.path.join(hl_sound_path, sound)):
			sounds.append(sound)
else:
	sounds = mod_sounds

print("Sounds that are going to be copied:", sounds)

###

gsr_file = '## Generated with Super Mod Converter 3000\n'

for sound in sounds:
	if sound[-3:] == 'txt':
		continue
	if not args.dry:
		shutil.copy(os.path.join(mod_sound_path, sound), os.path.join(out_sound_path, ntpath.split(sound)[0]))
	gsr_file += '\"{}\" \"{}\"\n'.format(os.path.join(sound), os.path.join(args.prefix, sound))
	if args.cm_override:
		gsr_file += '\"{}\" \"{}\"\n'.format(os.path.join('hlclassic', sound), os.path.join(args.prefix, sound))

if args.dry:
	print('Your .gsr file:')
	print(gsr_file)
else:
	gsr_path = os.path.join(out_path, 'maps', args.prefix + '.gsr')
	with open(gsr_path, 'w') as f:
		f.write(gsr_file)
	print('Don\'t forget to add "globalsoundlist" to you map\'s .cfg file!')

print('Done.')
