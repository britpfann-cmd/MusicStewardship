"""Transformation rule tests."""

from ingestion.rules import TransformationRule


def test_transformation_rule_can_be_created():
    rule = TransformationRule(
        field="title",
        operation="COPY",
    )

    assert rule is not None

def test_transformation_rule_preserves_field_and_operation():
    rule = TransformationRule(
        field="title",
        operation="COPY",
    )

    assert rule.field == "title"
    assert rule.operation == "COPY"

def test_transformation_rule_preserves_target_and_arguments():
    arguments = {"separator": " "}
    
    rule = TransformationRule(
        field="artist",
        operation="COMBINE",
        target="artist_name",
        arguments=arguments,
    )

    assert rule.target == "artist_name"
    assert rule.arguments == arguments

def test_transformation_rule_describe_returns_definition():
    rule = TransformationRule(
        field="artist",
        operation="COMBINE",
        target="artist_name",
        arguments={"separator": " "},
    )

    description = rule.describe()

    assert description["field"] == "artist"
    assert description["operation"] == "COMBINE"
    assert description["target"] == "artist_name"
    assert description["arguments"] == {"separator": " "}

def test_transformation_rule_defaults_are_empty():
    rule = TransformationRule(
        field="title",
        operation="COPY",
    )

    assert rule.target is None
    assert rule.arguments == {}

def test_transformation_rule_can_apply_decoder():
    class UpperDecoder:
        def decode(self, value, **kwargs):
            return value.upper()

    rule = TransformationRule(
        field="title",
        operation="COPY",
    )

    result = rule.apply(
        "example",
        decoder=UpperDecoder(),
    )

    assert result == "EXAMPLE"

def test_transformation_rule_passes_rule_to_decoder():
    class ContextDecoder:
        def decode(self, value, **kwargs):
            return kwargs["rule"]

    rule = TransformationRule(
        field="title",
        operation="COPY",
    )

    result = rule.apply(
        "example",
        decoder=ContextDecoder(),
    )

    assert result is rule

def test_transformation_rule_passes_arguments_to_decoder():
    class ContextDecoder:
        def decode(self, value, **kwargs):
            return kwargs["arguments"]

    arguments = {
        "separator": " / ",
        "components": ["ensemble", "performer"],
    }

    rule = TransformationRule(
        field="artist",
        operation="DECOMPOSE",
        arguments=arguments,
    )

    result = rule.apply(
        "Example Artist",
        decoder=ContextDecoder(),
    )
    

    assert result is arguments

def test_transformation_rule_can_decompose_with_decoder():
    from ingestion.decoders.compound import CompoundDecoder

    rule = TransformationRule(
        field="artist",
        operation="DECOMPOSE",
        arguments={
            "separator": " / ",
            "components": ["ensemble", "performer"],
        },
    )

    result = rule.apply(
        "Ensemble / Performer",
        decoder=CompoundDecoder(),
    )

    assert result == {
        "ensemble": "Ensemble",
        "performer": "Performer",
    }