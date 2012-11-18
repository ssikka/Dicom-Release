import os
import re
import csv
import sys
import shutil
import commands


def load_csv(csf_file):

    dicoms_per_scan = {}

    reader = csv.DictReader(open(csf_file, 'r'))

    for row in reader:

        dicoms_per_scan[row['scan']] = int(row['number_of_dicoms'])

    return dicoms_per_scan


def build_scan_dictionary(subject_path, scan_dirs, scans, dicoms_per_scan):

    scan_dict = {}


    for scan in scans.keys():

        for scan_dir in scan_dirs:


            scan_path = os.path.join(subject_path, scan_dir)

            num_dicoms = len(os.listdir(scan_path))

            if (scan in scan_dir) and (int(num_dicoms) == int(dicoms_per_scan[scan])):


                if scan in scan_dict:

                    val = scan_dict[scan]

                    val.append(scan_dir)

                    scan_dict[scan] = val

                else:

                    scan_dict[scan] = [scan_dir]

            elif (scan in scan_dir) and (num_dicoms != dicoms_per_scan[scan]):

                if not (('tensor' in scan_dir.lower()) or ('adc' in scan_dir.lower()) or ('fa' in scan_dir.lower()) or
                 ('trace' in scan_dir.lower()) or ('local' in scan_dir.lower()) or
                 ('dti' in scan_dir.lower()) or ('flair' in scan_dir.lower()) or ('range' in scan_dir.lower())):

                    f = open('./skipped_scans.txt', 'a')
                    print>>f, 'skipping '+ scan_path + ' actual # ' +str(num_dicoms) + ' expected: ' +str(dicoms_per_scan[scan])

    return scan_dict



def run(source_dir, target_dir, scans_csv):


    source_dir = os.path.abspath(sys.argv[1])
    target_dir = os.path.abspath(sys.argv[2])

    scans_csv = os.path.abspath(sys.argv[3])


    dicoms_per_scan = load_csv(scans_csv)

    scans = {'BREATH_HOLD_1400':'TfMRI_breathHold_1400', 'CHECKERBOARD_1400':'TfMRI_visualCheckerboard_1400',
             'CHECKERBOARD_645':'TfMRI_visualCheckerboard_645', 'DIFF_137_AP':'DTI_mx_137', 'MPRAGE':'anat',
             'REST_1400':'RfMRI_mx_1400', 'REST_645':'RfMRI_mx_645', 'REST_CAP':'RfMRI_std_2500'}

    subjects = os.listdir(source_dir)

    for subject in subjects:


        subject_path = os.path.join(source_dir, subject)

        scan_dirs = os.listdir(subject_path)


        scan_dict = build_scan_dictionary(subject_path, list(scan_dirs), dict(scans), dicoms_per_scan)

        for scan_orig, scan_dirs in scan_dict.items():

            if len(scan_dirs) == 1:


                try:
                    scan_d = os.path.join(subject, scans[scan_orig])
                    target = os.path.join(target_dir, scan_d)

                    if not (('TfMRI' in target) or ('anat' in target)):
                        scan_d = os.path.join(subject, os.path.join('session_1', scans[scan_orig]))
                    target = os.path.join(target_dir, scan_d)
                    source = os.path.join(source_dir, os.path.join(subject, scan_dirs[0]))

                    print 'moving ', source, ' -> ', target
                    shutil.copytree(source, target)
                except:

                    print 'already exists: ', target

            else:

                dir = None

                value = None

                i = 0
                for scan_dir in scan_dirs:

                    s_f, val = scan_dir.rsplit('_', 1)

                    v1 = int(re.findall(r'\d+', val)[0])
                    if i > 0:

                        if v1 > value:
                            dir = scan_dir
                            value = v1
                    else:
                        dir = scan_dir
                        value = v1

                    i += 1

                try:
                    scan_d = os.path.join(subject, scans[scan_orig])
                    target = os.path.join(target_dir, scan_d)

                    if not (('TfMRI' in target) or ('anat' in target)):
                        scan_d = os.path.join(subject, os.path.join('session_1', scans[scan_orig]))
                    target = os.path.join(target_dir, scan_d)
                    source = os.path.join(source_dir, os.path.join(subject, dir))
                    print 'moving ', source, ' -> ', target
                    shutil.copytree(source, target)

                except:

                    print 'already exists: ', os.path.join(target)

