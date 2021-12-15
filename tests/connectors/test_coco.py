from eto.connectors.coco import CocoConfig, CocoConnector, CocoSource


def test_coco():
    c = CocoConnector(None)
    assert c.connector_type == "coco"
    c.project_id = "default"
    c.dataset_id = "dataset"
    c.partition = "split"
    c.mode = "append"
    c.add_source(
        CocoSource(
            image_dir="s3://images",
            annotation="s3://annotations",
            extras={"foo": "bar"},
        )
    )
    request = c.request_body
    assert request.config.dataset_name == "default.dataset"
    assert request.config.mode == "append"
    assert tuple(request.config.partition) == ("split",)
    assert request.config.source[0].image_dir == "s3://images"
    assert request.config.source[0].annotation == "s3://annotations"
    assert request.config.source[0].extras == {"foo": "bar"}
