#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
taffmat.py

Read and write Teac TAFFmat files.

The .dat file is read into a numpy array.
The .hdr file is read into an OrderedDict

Per the Teac LX-10 Instruction Manual, the A/D-converted data
is recored as 2-byte integers from -32,768 to +32,767. Negative
numbers are expressed as 2's complements. The byte order is from
the lower bytes to the higher bytes.

The max ADC values are +/-25,000, which represents +/-100% of
the input range (i.e., slope = range / 25000):

     0.5V = 2e-5
       1V = 4e-5
       2V = 8e-5
       5V = 2e-4
      10V = 4e-4
      20V = 8e-4
      50V = 2e-3

# Notes on the header file format #

* If the voice memo recording is off, then the VOICE_MEMO line will
be absent from the header file.
* The MEMO_LENGTH and MEMO lines are *not* related to the voice memo.
Those are for the memo field. The MEMO_LENGTH line contains
an integer of the number of characters on the MEMO line and
then has 7 zeros comma separated afterwards.
* Some HDR files have two blank lines at the end with the last line containing
three spaces (line above that contains nothing). Other HDR files appear
to just have one blank line at the end with no spaces on it.
* The binary Teac data is stored as int16 (2-bytes) and only
+25,000 to -25,000 and then it's multiplied by the slope,
which we know can be 0.5, 1, 2, 5, 10, 20 or 50 V. Note that,
"a range of +/-131% of the selected range can be obtained for 
A/D conversion value; however, the input margin
level is approximately +/-120%." [Source p. 4-5 of Teac manual]

"""

# FIXME: Need to convert this from a module to its own package.

# Try to future proof code so that it's Python 3.x ready
from __future__ import print_function
# unicode_literals caused a matplotlib failure I believe,
# so watch for errors
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

# Standard module imports
import os
from datetime import datetime
from collections import OrderedDict

# Data analysis related imports
import numpy as np

def _apply_slope_and_offset(data_array, number_of_series, slope, y_offset):
    """
    Convert from int16 to float64 and apply the slope and offset
    so the data_array contains the measured values.
    """
    data_array = data_array.astype(np.float64)
    for series in range(0, number_of_series):
        data_array[series] = (data_array[series] * slope[series] 
                + y_offset[series])

    return data_array

def _remove_slope_and_offset(data_array, number_of_series, slope, y_offset):
    """
    Convert data_array from float64 to int16 by removing the slope and offset
    in preparation to writing the TAFFmat .dat file
    """
    print(type(y_offset[0]))
    for series in range(0, number_of_series):
        data_array[series] = np.around((data_array[series] - y_offset[series]) /
                slope[series])

    data_array = data_array.astype('int16')

    return data_array

def _format_exponent_notation(input_number, precision, num_exponent_digits):
    """
    Format the exponent notation. Python's exponent notation doesn't allow
    for a user-defined number of exponent digits.

    Based on [Anurag Uniyal's answer][answer] to the StackOverflow
    question ['Python - number of digits in exponent'][question]

    [question]: http://stackoverflow.com/q/9910972/95592
    [answer]: http://stackoverflow.com/a/9911741/95592
    """
    python_exponent_notation = '{number:.{precision}e}'.format(
            number=input_number,
            precision=precision)
    print("Here 1", python_exponent_notation)
    mantissa, exponent = python_exponent_notation.split('e')
    # Add 1 to the desired number of exponenent digits to account for the sign
    return '{mantissa}e{exponent:+0{exp_num}d}'.format(
            mantissa=mantissa,
            exponent=int(exponent),
            exp_num=num_exponent_digits+1)

def read_taffmat(input_file):

    input_file_basename, input_file_extension = os.path.splitext(
            input_file)

    inputdatfile = '{base}.dat'.format(base=input_file_basename)
    inputhdrfile = '{base}.hdr'.format(base=input_file_basename)

    if not os.path.isfile(inputdatfile) or not os.path.isfile(inputhdrfile):
        return False

    # Process the header file first
    with open(inputhdrfile, 'r') as f_header:
        header_data_all_lines = f_header.readlines()

    # Read the header file into an ordered dictionary using the first
    # word of each line as the key.
    raw_header_data = OrderedDict()
    for line in header_data_all_lines:
        try:
            [key, data] = line.split(' ', 1)
            if key is not '':
                if key.lower() in raw_header_data:
                    raw_header_data[key.lower() + '2'] = data.strip()
                else:
                    raw_header_data[key.lower()] = data.strip()
        except:
            raw_header_data[line.lower().strip()] = ''

    # Create a "smarter" dictionary based on the raw_header_data
    header_data = OrderedDict()
    header_data['dataset'] = raw_header_data['dataset']
    header_data['version'] = int(raw_header_data['version'])
    header_data['series_labels'] = raw_header_data['series'].split(',')
    start_recording_datetime_as_string = (raw_header_data['date'] + 
            ' ' + raw_header_data['time'])
    header_data['recording_start_datetime'] = datetime.strptime(
            start_recording_datetime_as_string, '%m-%d-%Y %H:%M:%S.%f')
    header_data['sampling_frequency_hz'] = int(raw_header_data['rate'])
    header_data['vertical_units'] = raw_header_data['vert_units'].split(',')
    header_data['horizontal_units'] = raw_header_data['horz_units']
    header_data['comment'] = raw_header_data['comment']
    header_data['number_of_series'] = int(raw_header_data['num_series'])
    header_data['storage_mode'] = raw_header_data['storage_mode']
    header_data['file_type'] = raw_header_data['file_type']
    header_data['slope'] = [float(slope)
            for slope in raw_header_data['slope'].split(',')]
    header_data['x_offset'] = float(raw_header_data['x_offset'])
    header_data['y_offset'] = [float(y_offset)
            for y_offset in raw_header_data['y_offset'].split(',')]
    header_data['number_of_samples'] = int(raw_header_data['num_samps'])
    header_data['device'] = raw_header_data['device']
    slot1_amp = raw_header_data['slot1_amp'].split(',')
    header_data['slot1_amp'] = {}
    header_data['slot1_amp']['id_name'] = slot1_amp[0]
    header_data['slot1_amp']['num_of_channels'] = slot1_amp[1]
    header_data['slot1_amp']['pld_version'] = slot1_amp[2].strip()
    header_data['slot1_amp']['firmware_version'] = slot1_amp[3].strip()
    header_data['slot2_amp'] = {}
    slot2_amp = raw_header_data['slot2_amp'].split(',')
    header_data['slot2_amp']['id_name'] = slot2_amp[0]
    header_data['slot2_amp']['num_of_channels'] = slot2_amp[1]
    header_data['slot2_amp']['pld_version'] = slot2_amp[2].strip()
    header_data['slot2_amp']['firmware_version'] = slot2_amp[3].strip()
    header_data['channel_info'] = []
    for index in range(header_data['number_of_series']):
        raw_key = 'ch{channel_num}_{channel_num}'.format(
                channel_num = index + 1)
        raw_channel_info = raw_header_data[raw_key].split(',')
        header_data['channel_info'].append({
            'channel_num': index + 1,
            'amp_type': raw_channel_info[0],
            'range_setting': raw_channel_info[1],
            'filter_setting': raw_channel_info[2]})
    header_data['id_num'] = int(raw_header_data['id_no'])
    start_time, end_time = raw_header_data['time2'].split(',')
    header_data['start_time'] = int(start_time)
    header_data['stop_time'] = int(end_time)
    header_data['recording_destination'] = raw_header_data['rec_mode']
    # FIXME: Need to properly parse the start trigger and stop condition
    # Right now I'm basically assuming they're not used in the data.
    header_data['start_trigger'] = raw_header_data['start_trigger']
    header_data['stop_condition'] = raw_header_data['stop_condition']
    # FIXME: Need to change so that we can handle more than just
    # LX-10 files. The Teac documentation states this will be one of:
    # LX10_VERSION, LX20_VERSION, LX110_VERSION, or LX120_VERSION
    # FIXME: If we change to handle LX-110 or LX-120, we'll probably
    # need to change from assuming int16 to determing if the data
    # was stored as either int16 or int32.
    # FIXME: Need to handle both when the memo is ON and OFF.
    # For memo on, we'll have a key of voice_memo in the raw_header_data
    # dictionary, whereas, if the memo is off that key will not exist
    if 'voice_memo' in raw_header_data:
        # Voice memo was recorded
        header_data['voice_memo_on'] = True
        voice_memo_temp = raw_header_data['voice_memo'].split(',')
        header_data['voice_memo_bits_per_sample'] = voice_memo_temp[0]
        header_data['voice_memo_size_bytes'] = int(voice_memo_temp[1])
    else:
        # Voice memo was not recored
        header_data['voice_memo_on'] = False
    header_data['lx10_version'] = raw_header_data['lx10_version']
    header_data['memo_length'] = raw_header_data['memo_length']
    header_data['memo'] = raw_header_data['memo']

    # Time to process the dat file
    # Read the entire file and reshape the data so that each channel/series
    # is in its own row
    with open(inputdatfile, 'rb') as datfile:
        data_array = np.fromfile(datfile, np.int16).reshape((-1,header_data['number_of_series'])).T

    data_array = _apply_slope_and_offset(data_array,
            header_data['number_of_series'],
            header_data['slope'],
            header_data['y_offset'])

    # Create the array for the time/x dimension
    time_vector = np.linspace(0, 
            header_data['number_of_samples'] / header_data['sampling_frequency_hz'],
            header_data['number_of_samples'])

    return (data_array, time_vector, header_data)


def write_taffmat(data_array, header_data, output_base_filename):

    # Determine the output file names
    output_hdr_filename = '{base}.hdr'.format(base=output_base_filename)
    output_dat_filename = '{base}.dat'.format(base=output_base_filename)

    # Convert "smart" dictionary items into strings that are
    # ready to be saved to the .hdr text file.
    header_output = []
    header_output.append('DATASET ' + header_data['dataset'] + '\n')
    header_output.append('VERSION ' + str(header_data['version']) + '\n')
    header_output.append('SERIES ' + ','.join(header_data['series_labels']) + ' \n')
    header_output.append('DATE ' + header_data['recording_start_datetime'].strftime('%m-%d-%Y') + '\n')
    header_output.append('TIME ' + 
            header_data['recording_start_datetime'].strftime('%H:%M:%S.%f')[0:11] + '\n')
    header_output.append('RATE ' + str(header_data['sampling_frequency_hz']) + '\n')
    header_output.append('VERT_UNITS ' + ','.join(header_data['vertical_units']) + ' \n')
    header_output.append('HORZ_UNITS ' + header_data['horizontal_units'] + '\n')
    header_output.append('COMMENT ' + header_data['comment'] + '\n')
    header_output.append('NUM_SERIES ' + str(header_data['number_of_series']) + '\n')
    header_output.append('STORAGE_MODE ' + header_data['storage_mode'] + '\n')
    header_output.append('FILE_TYPE ' + header_data['file_type'] + '\n')
    header_output.append('SLOPE ' + ','.join(
        [_format_exponent_notation(slope, 6, 3) for slope in header_data['slope']]) + ' \n')
    header_output.append('X_OFFSET {:1.1f}\n'.format(header_data['x_offset']))
    header_output.append('Y_OFFSET ' + ','.join(
        [_format_exponent_notation(y_offset, 6, 3) for y_offset in header_data['y_offset']]) + ' \n')
    header_output.append('NUM_SAMPS {}\n'.format(header_data['number_of_samples']))
    header_output.append('DATA\n')
    header_output.append('DEVICE {}\n'.format(header_data['device']))
    # FIXME: Need to add two spaces to the end of the firmware_version (8 fixed spaces)
    # if the firmware_version is not blank. If the firmware_version is blank,
    # then the line ends with the comma
    header_output.append('SLOT1_AMP {id},{num_ch},{pld_ver},{fw_ver}\n'.format(
        id=header_data['slot1_amp']['id_name'],
        num_ch=header_data['slot1_amp']['num_of_channels'],
        pld_ver=header_data['slot1_amp']['pld_version'].ljust(8,' '),
        fw_ver=header_data['slot1_amp']['firmware_version'].ljust(8,' ')))
    header_output.append('SLOT2_AMP {id},{num_ch},{pld_ver},{fw_ver}\n'.format(
        id=header_data['slot2_amp']['id_name'],
        num_ch=header_data['slot2_amp']['num_of_channels'],
        pld_ver=header_data['slot2_amp']['pld_version'],
        fw_ver=header_data['slot2_amp']['firmware_version']))
    for index in range(header_data['number_of_series']):
        channel_key = 'CH{channel_num}_{channel_num}'.format(
                channel_num = index + 1)
        header_output.append('{channel_key} {amp_type},{range_setting},{filter_setting}\n'.format(
            channel_key=channel_key,
            amp_type=header_data['channel_info'][index]['amp_type'],
            range_setting=header_data['channel_info'][index]['range_setting'],
            filter_setting=header_data['channel_info'][index]['filter_setting']))
    header_output.append('ID_NO {id_num}\n'.format(id_num=header_data['id_num']))
    header_output.append('TIME {start},{end}\n'.format(
        start=header_data['start_time'],
        end=header_data['stop_time']))
    header_output.append('REC_MODE {rec_mode} \n'.format(
        rec_mode=header_data['recording_destination']))
    header_output.append('START_TRIGGER {trigger}  \n'.format(
        trigger=header_data['start_trigger']))
    header_output.append('STOP_CONDITION {condition}  \n'.format(
        condition=header_data['stop_condition']))
    header_output.append('ID_END\n')
    if header_data['voice_memo_on']:
        header_output.append('VOICE_MEMO {bits},{size}\n'.format(
            bits=header_data['voice_memo_bits_per_sample'],
            size=header_data['voice_memo_size_bytes']))
    header_output.append('LX10_VERSION {ver}\n'.format(
        ver=header_data['lx10_version']))
    header_output.append('MEMO_LENGTH {memo_len}\n'.format(
        memo_len=header_data['memo_length']))
    header_output.append('MEMO {memo}\n'.format(memo=header_data['memo']))
    header_output.append('\n')


    # Write the .hdr file
    with open(output_hdr_filename, 'w') as f_header:
        f_header.writelines(header_output)


    # Convert data_array into int16 values by removing the offset
    # and slope, such that +/-100% = +/-25,000 int16
    # Then write the binary data file.
    data_array = _remove_slope_and_offset(data_array,
            header_data['number_of_series'],
            header_data['slope'],
            header_data['y_offset'])
    with open(output_dat_filename, 'wb') as datfile:
        data_array.T.reshape((-1,header_data['number_of_series'])).tofile(datfile)

    return


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfile', 
            action="store",
            help="Input filename excluding extension")
    parser.add_argument('-o', '--outputfile', 
            action="store",
            help="Output filename including extension")
    args = parser.parse_args()

    input_file_basename, input_file_extension = os.path.splitext(os.path.realpath(args.inputfile))
    if args.outputfile is None:
        outputfile = '{base}.csv'.format(base=input_file_basename)
    else:
        outputfile = os.path.realpath(args.outputfile)

    print("Start reading the TAFFmat file")
    data_array, time_vector, header_data = read_taffmat(input_file_basename)

    # Print some information about the data we just grabbed
    print("Sampled {num_samples:,} samples over {sample_time:.3f} sec at {sampling_freq:,} Hz".format(
        num_samples = header_data['number_of_samples'],
        sample_time = header_data['number_of_samples'] / header_data['sampling_frequency_hz'],
        sampling_freq = header_data['sampling_frequency_hz']))
    print("Resulting in {sec_per_sample:.4e} sec/sample".format(
        sec_per_sample = 1 / header_data['sampling_frequency_hz']))

