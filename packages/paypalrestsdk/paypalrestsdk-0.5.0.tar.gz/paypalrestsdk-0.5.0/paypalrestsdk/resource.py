import paypalrestsdk.util as util
import paypalrestsdk.api  as api
import uuid

# Base class for all REST service
class Resource(dict):

  convert_resources = {}

  def __init__(self, attributes = {}):
    super(Resource, self).__setattr__('error', None)
    super(Resource, self).__setattr__('headers', {})
    super(Resource, self).__setattr__('header', {})
    super(Resource, self).__setattr__('request_id', None)
    self.merge(attributes)

  # Generate uniq request id
  def generate_request_id(self):
    if self.request_id == None :
      self.request_id = str(uuid.uuid4())
    return self.request_id

  # Generate HTTP header
  def http_headers(self):
    return util.merge_dict(self.header, self.headers,
        { 'PayPal-Request-Id': self.generate_request_id() })

  # Getter
  def __getattr__(self, name):
    return self.get(name)

  # Setter
  def __setattr__(self, name, value):
    value = self.convert(name, value)
    try:
      # Handle attributes(error, header, request_id)
      super(Resource, self).__getattribute__(name)
      super(Resource, self).__setattr__(name, value)
    except AttributeError:
      self[name] = value

  # return True if no error
  def success(self):
    return self.error == None

  # Merge new attributes
  def merge(self, new_attributes):
    for k in new_attributes:
      self.__setattr__(k, new_attributes[k])

  # Convert the attribute values to configured class.
  def convert(self, name, value):
    if isinstance(value, dict):
      klass = self.convert_resources.get(name, Resource)
      return klass(value)
    elif isinstance(value, list):
      new_list = []
      for obj in value:
        new_list.append(self.convert(name, obj))
      return new_list
    else:
      return value

# == Example
#   payment = Payment.find("PAY-1234")
class Find(Resource):
  @classmethod
  def find(klass, resource_id):
    url = util.join_url(klass.path, str(resource_id))
    return klass(api.default().get(url))

# == Example
#   payment_histroy = Payment.all({'count': 2})
class List(Resource):
  list_class = Resource

  @classmethod
  def all(klass, params = None):
    if params == None:
      url = klass.path
    else:
      url = util.join_url_params(klass.path, params)
    return klass.list_class(api.default().get(url))

# == Example
#   payment = Payment({})
#   payment.create() # return True or False
class Create(Resource):
  def create(self):
    new_attributes = api.default().post(self.path, self, self.http_headers())
    self.error = None
    self.merge(new_attributes)
    return self.success()

# == Example
#   payment.post("execute", {'payer_id': '1234'}, payment)  # return True or False
#   sale.post("refund", {'payer_id': '1234'})  # return Refund object
class Post(Resource):
  def post(self, name, attributes = {}, klass = Resource):
    url = util.join_url(self.path, str(self['id']), name)
    if not isinstance(attributes, Resource):
      attributes = Resource(attributes)
    new_attributes = api.default().post(url, attributes, attributes.http_headers())
    if isinstance(klass, Resource):
      klass.error = None
      klass.merge(new_attributes)
      return self.success()
    else:
      return klass(new_attributes)
