import argparse
import os
import sys

import subprocess
from os.path import expanduser
PROTO_CACHE = expanduser("~/Library/Caches/com.apple.UserStudies.proto")

class SensorKitProtoFile(object):
    """
    Utility to parse proto object files uploaded to HealthCloud by SensorKit
    The files should be in u_s_s_r.proto encoded
    """
    def __init__(self, data_file_path, proto_file_path=None):
        """
        :param data_file_path: Path to file to be decoded
        :param proto_file_path: Path to protobuf specification u_s_s_r.proto
        """
        if not proto_file_path:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            proto_file_path = os.path.join(current_dir, "u_s_s_r_proto.proto")

        self.proto_file_path = expanduser(proto_file_path)
        self.data_file_path = expanduser(data_file_path)

        self.file_object = open(self.proto_file_path, "rb")

        # To hold the metadata read from MSL file
        self.payload_metadata = None
        self.device = None

    def decode_proto(self):
        """
        Compiles protobuf specification "u_s_s_r_proto.proto" and
        creates necessary Python libraries. Compiled python modules are also added
        to System path.
        :return:
        """
        # Create output directory it does not exist
        if not os.path.exists(PROTO_CACHE):
            os.makedirs(PROTO_CACHE)

        # Compile proto (TODO: Assumes protoc is in PATH)
        cmd = "protoc -I {} --python_out={} {}".format(
            os.path.dirname(self.proto_file_path),
            PROTO_CACHE,
            self.proto_file_path)
        subprocess.check_call(cmd, shell=True)

        # Append compiled python module to Python's system path
        sys.path.insert(0, PROTO_CACHE)
        globals()["ProtoDefinition"] = __import__("u_s_s_r_proto_pb2")

    def walk(self):
        """
        Iterator to return one record at a time.
        Assigns payload and device metadata to the instance of SensorKitProtoFile
        :return:
        """
        data = open(self.data_file_path, 'rb')
        read_metric = globals()["ProtoDefinition"].Payload()
        read_metric.ParseFromString(data.read())

        # One record for the whole file
        self.payload_metadata = read_metric.payloadMetadata
        self.device = read_metric.device

        # Get list of all *repeated* field types
        field_names = []
        for field_desc in read_metric.DESCRIPTOR.fields:
            field_name = field_desc.name

            if field_desc.label == field_desc.LABEL_REPEATED:
                field_names.append(field_name)

        # For each repeated field type, get the data and yield one item at a time
        for field_name in field_names:
            stream_samples = getattr(read_metric, field_name)
            for sample in stream_samples:
                yield self.device, sample


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Print protos uploaded by UserStudyFramework to HealthCloud')
    parser.add_argument('--data', '-d', dest="data_path", default=None, required=True)
    parser.add_argument('--proto', '-s', dest="proto_path", default=None, required=False)
    args = parser.parse_args()

    # Check if arguments are well formed
    if not os.path.exists(args.data_path):
        print "Cant find msl file"
        sys.exit(-1)

    # Walk data file
    sensorkit_proto_parser = SensorKitProtoFile(args.data_path, args.proto_path)
    sensorkit_proto_parser.decode_proto()
    for r in sensorkit_proto_parser.walk():
        print r
