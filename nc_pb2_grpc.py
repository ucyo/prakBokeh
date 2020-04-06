# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import nc_pb2 as nc__pb2


class NCServiceStub(object):
    """Missing associated documentation comment in .proto file"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetHeightProfile = channel.unary_unary(
                '/nc.NCService/GetHeightProfile',
                request_serializer=nc__pb2.HeightProfileRequest.SerializeToString,
                response_deserializer=nc__pb2.HeightProfileReply.FromString,
                )
        self.GetAggValuesPerLon = channel.unary_unary(
                '/nc.NCService/GetAggValuesPerLon',
                request_serializer=nc__pb2.AggValuesPerLonRequest.SerializeToString,
                response_deserializer=nc__pb2.AggValuesPerLonReply.FromString,
                )
        self.GetMesh = channel.unary_unary(
                '/nc.NCService/GetMesh',
                request_serializer=nc__pb2.MeshRequest.SerializeToString,
                response_deserializer=nc__pb2.MeshReply.FromString,
                )
        self.GetTris = channel.unary_unary(
                '/nc.NCService/GetTris',
                request_serializer=nc__pb2.TrisRequest.SerializeToString,
                response_deserializer=nc__pb2.TrisReply.FromString,
                )
        self.GetTrisAgg = channel.unary_unary(
                '/nc.NCService/GetTrisAgg',
                request_serializer=nc__pb2.TrisAggRequest.SerializeToString,
                response_deserializer=nc__pb2.TrisReply.FromString,
                )


class NCServiceServicer(object):
    """Missing associated documentation comment in .proto file"""

    def GetHeightProfile(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAggValuesPerLon(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMesh(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetTris(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetTrisAgg(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_NCServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetHeightProfile': grpc.unary_unary_rpc_method_handler(
                    servicer.GetHeightProfile,
                    request_deserializer=nc__pb2.HeightProfileRequest.FromString,
                    response_serializer=nc__pb2.HeightProfileReply.SerializeToString,
            ),
            'GetAggValuesPerLon': grpc.unary_unary_rpc_method_handler(
                    servicer.GetAggValuesPerLon,
                    request_deserializer=nc__pb2.AggValuesPerLonRequest.FromString,
                    response_serializer=nc__pb2.AggValuesPerLonReply.SerializeToString,
            ),
            'GetMesh': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMesh,
                    request_deserializer=nc__pb2.MeshRequest.FromString,
                    response_serializer=nc__pb2.MeshReply.SerializeToString,
            ),
            'GetTris': grpc.unary_unary_rpc_method_handler(
                    servicer.GetTris,
                    request_deserializer=nc__pb2.TrisRequest.FromString,
                    response_serializer=nc__pb2.TrisReply.SerializeToString,
            ),
            'GetTrisAgg': grpc.unary_unary_rpc_method_handler(
                    servicer.GetTrisAgg,
                    request_deserializer=nc__pb2.TrisAggRequest.FromString,
                    response_serializer=nc__pb2.TrisReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'nc.NCService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class NCService(object):
    """Missing associated documentation comment in .proto file"""

    @staticmethod
    def GetHeightProfile(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nc.NCService/GetHeightProfile',
            nc__pb2.HeightProfileRequest.SerializeToString,
            nc__pb2.HeightProfileReply.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetAggValuesPerLon(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nc.NCService/GetAggValuesPerLon',
            nc__pb2.AggValuesPerLonRequest.SerializeToString,
            nc__pb2.AggValuesPerLonReply.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetMesh(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nc.NCService/GetMesh',
            nc__pb2.MeshRequest.SerializeToString,
            nc__pb2.MeshReply.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetTris(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nc.NCService/GetTris',
            nc__pb2.TrisRequest.SerializeToString,
            nc__pb2.TrisReply.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetTrisAgg(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nc.NCService/GetTrisAgg',
            nc__pb2.TrisAggRequest.SerializeToString,
            nc__pb2.TrisReply.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)
