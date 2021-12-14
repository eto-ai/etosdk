from eto.connectors.coco import CocoSource, CocoConnector


def test_source():
    s = CocoSource('s3://images', 's3//annotations', {'foo': 'bar'})
    assert s.to_dict() == {
        'image_dir': 's3://images',
        'annotation': 's3//annotations',
        'extras': {'foo': 'bar'}
    }


def test_coco():
    c = CocoConnector(None)
    assert c.connector_type == 'coco'
    c.dataset_id = 'dataset'
    c.add_source(CocoSource('s3://images', 's3://annotations', {'foo': 'bar'}))
    request = c.request_body
    assert request.config == {
        'dataset_name': 'default.dataset',
        'mode': 'error',
        'partition': None,
        'source': [{'image_dir': 's3://images',
                    'annotation': 's3://annotations',
                    'extras': {'foo': 'bar'}}]}
