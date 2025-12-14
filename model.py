import redis
from redis.commands.search.field import NumericField,TextField,TagField
from redis.commands.search.index_definition import IndexDefinition, IndexType

r=redis.Redis(host="127.0.0.1",port="6379",db=0,decode_responses=True)

schema=(
    NumericField("$.UID",as_name="UID"),
    TextField("$.savedFileURL",as_name="savedFileURL"),
    TagField("$.processComplete",as_name="processComplete"),
)