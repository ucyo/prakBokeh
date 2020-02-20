# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import nc_pb2 as nc__pb2


class NCServiceStub(object):
  # missing associated documentation comment in .proto file
  pass

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
  # missing associated documentation comment in .proto file
  pass

  def GetHeightProfile(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetAggValuesPerLon(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetMesh(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetTris(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetTrisAgg(self, request, context):
    # missing associated documentation comment in .proto file
    pass
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