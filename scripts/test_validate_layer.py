"""Tests for the BSP layer validation tool."""

import os
import tempfile

import pytest

from validate_layer import (
    check_bbappend_targets,
    check_conf_variables,
    check_dependencies,
    check_layer_priority,
    check_layerseries_compat,
    check_missing_includes,
    check_recipe_syntax,
    find_files,
    validate_layer,
)


@pytest.fixture
def tmp_layer(tmp_path):
    """Create a minimal valid layer structure."""
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()

    layer_conf = conf_dir / "layer.conf"
    layer_conf.write_text(
        'BBPATH .= ":${LAYERDIR}"\n'
        'BBFILES += "${LAYERDIR}/recipes-*/*/*.bb"\n'
        'BBFILE_COLLECTIONS += "test-layer"\n'
        'BBFILE_PATTERN_test-layer = "^${LAYERDIR}/"\n'
        'BBFILE_PRIORITY_test-layer = "6"\n'
        'LAYERSERIES_COMPAT_test-layer = "scarthgap"\n'
    )
    return tmp_path


@pytest.fixture
def tmp_layer_with_recipes(tmp_layer):
    """Create a layer with sample recipes."""
    recipe_dir = tmp_layer / "recipes-example" / "example"
    recipe_dir.mkdir(parents=True)

    bb_file = recipe_dir / "example_1.0.bb"
    bb_file.write_text(
        'SUMMARY = "Example recipe"\n'
        'LICENSE = "MIT"\n'
        'DEPENDS = "zlib"\n'
    )
    return tmp_layer


class TestFindFiles:
    def test_find_bb_files(self, tmp_layer_with_recipes):
        results = find_files(str(tmp_layer_with_recipes), [".bb"])
        assert len(results) == 1
        assert results[0].endswith(".bb")

    def test_find_no_matching_files(self, tmp_layer):
        results = find_files(str(tmp_layer), [".bb"])
        assert len(results) == 0

    def test_find_conf_files(self, tmp_layer):
        results = find_files(str(tmp_layer), [".conf"])
        assert len(results) == 1


class TestCheckRecipeSyntax:
    def test_valid_recipe(self, tmp_layer_with_recipes):
        errors = check_recipe_syntax(str(tmp_layer_with_recipes))
        assert len(errors) == 0

    def test_unmatched_quote(self, tmp_layer):
        recipe_dir = tmp_layer / "recipes-test" / "test"
        recipe_dir.mkdir(parents=True)
        bad_recipe = recipe_dir / "bad_1.0.bb"
        bad_recipe.write_text('SUMMARY = "Unmatched quote\n')

        errors = check_recipe_syntax(str(tmp_layer))
        assert any("Unmatched double quote" in e for e in errors)

    def test_unclosed_function(self, tmp_layer):
        recipe_dir = tmp_layer / "recipes-test" / "test"
        recipe_dir.mkdir(parents=True)
        bad_recipe = recipe_dir / "bad_1.0.bb"
        bad_recipe.write_text('do_install() {\n    echo "hello"\n')

        errors = check_recipe_syntax(str(tmp_layer))
        assert any("Unclosed function" in e for e in errors)

    def test_no_recipes(self, tmp_layer):
        errors = check_recipe_syntax(str(tmp_layer))
        assert len(errors) == 0


class TestCheckDependencies:
    def test_valid_deps(self, tmp_layer_with_recipes):
        errors = check_dependencies(str(tmp_layer_with_recipes))
        assert len(errors) == 0

    def test_suspicious_dep_chars(self, tmp_layer):
        recipe_dir = tmp_layer / "recipes-test" / "test"
        recipe_dir.mkdir(parents=True)
        recipe = recipe_dir / "test_1.0.bb"
        recipe.write_text('DEPENDS = "valid-dep some@bad"\n')

        errors = check_dependencies(str(tmp_layer))
        assert any("Suspicious dependency" in e for e in errors)


class TestCheckLayerseriesCompat:
    def test_valid_compat(self, tmp_layer):
        errors = check_layerseries_compat(str(tmp_layer))
        assert len(errors) == 0

    def test_unknown_release(self, tmp_layer):
        layer_conf = tmp_layer / "conf" / "layer.conf"
        layer_conf.write_text(
            'LAYERSERIES_COMPAT_test = "scarthgap fakebranch"\n'
        )

        errors = check_layerseries_compat(str(tmp_layer))
        assert any("Unknown Yocto release" in e for e in errors)
        assert any("fakebranch" in e for e in errors)

    def test_missing_compat(self, tmp_layer):
        layer_conf = tmp_layer / "conf" / "layer.conf"
        layer_conf.write_text('BBFILE_COLLECTIONS += "test"\n')

        errors = check_layerseries_compat(str(tmp_layer))
        assert any("LAYERSERIES_COMPAT not defined" in e for e in errors)

    def test_missing_layer_conf(self, tmp_path):
        errors = check_layerseries_compat(str(tmp_path))
        assert any("Missing conf/layer.conf" in e for e in errors)


class TestCheckBbappendTargets:
    def test_bbappend_without_bb(self, tmp_layer):
        recipe_dir = tmp_layer / "recipes-test" / "test"
        recipe_dir.mkdir(parents=True)
        bbappend = recipe_dir / "missing_1.0.bbappend"
        bbappend.write_text('FILESEXTRAPATHS:prepend := "${THISDIR}:"\n')

        errors = check_bbappend_targets(str(tmp_layer))
        assert any("No matching .bb recipe" in e for e in errors)

    def test_bbappend_with_matching_bb(self, tmp_layer):
        recipe_dir = tmp_layer / "recipes-test" / "test"
        recipe_dir.mkdir(parents=True)
        bb = recipe_dir / "myrecipe_1.0.bb"
        bb.write_text('SUMMARY = "test"\n')
        bbappend = recipe_dir / "myrecipe_1.0.bbappend"
        bbappend.write_text('EXTRA_OECONF += "--enable-foo"\n')

        errors = check_bbappend_targets(str(tmp_layer))
        assert len(errors) == 0

    def test_bbappend_wildcard(self, tmp_layer):
        recipe_dir = tmp_layer / "recipes-test" / "test"
        recipe_dir.mkdir(parents=True)
        bb = recipe_dir / "myrecipe_1.0.bb"
        bb.write_text('SUMMARY = "test"\n')
        bbappend = recipe_dir / "myrecipe_%.bbappend"
        bbappend.write_text('SRC_URI += "file://patch.patch"\n')

        errors = check_bbappend_targets(str(tmp_layer))
        assert len(errors) == 0


class TestCheckConfVariables:
    def test_valid_conf(self, tmp_layer):
        errors = check_conf_variables(str(tmp_layer))
        assert len(errors) == 0

    def test_missing_collection(self, tmp_layer):
        layer_conf = tmp_layer / "conf" / "layer.conf"
        layer_conf.write_text('BBPATH .= ":${LAYERDIR}"\n')

        errors = check_conf_variables(str(tmp_layer))
        assert any("BBFILE_COLLECTIONS" in e for e in errors)

    def test_missing_layer_conf(self, tmp_path):
        errors = check_conf_variables(str(tmp_path))
        assert any("Missing conf/layer.conf" in e for e in errors)


class TestCheckLayerPriority:
    def test_valid_priority(self, tmp_layer):
        errors = check_layer_priority(str(tmp_layer))
        assert len(errors) == 0

    def test_priority_out_of_range(self, tmp_layer):
        layer_conf = tmp_layer / "conf" / "layer.conf"
        layer_conf.write_text('BBFILE_PRIORITY_test = "100"\n')

        errors = check_layer_priority(str(tmp_layer))
        assert any("outside valid range" in e for e in errors)

    def test_missing_priority(self, tmp_layer):
        layer_conf = tmp_layer / "conf" / "layer.conf"
        layer_conf.write_text('BBFILE_COLLECTIONS += "test"\n')

        errors = check_layer_priority(str(tmp_layer))
        assert any("BBFILE_PRIORITY not defined" in e for e in errors)

    def test_missing_layer_conf(self, tmp_path):
        errors = check_layer_priority(str(tmp_path))
        assert any("Missing conf/layer.conf" in e for e in errors)


class TestCheckMissingIncludes:
    def test_valid_include(self, tmp_layer):
        inc_dir = tmp_layer / "conf" / "distro" / "include"
        inc_dir.mkdir(parents=True)
        inc_file = inc_dir / "common.inc"
        inc_file.write_text('EXTRA_VAR = "value"\n')

        conf_file = tmp_layer / "conf" / "distro" / "test.conf"
        conf_file.write_text("require conf/distro/include/common.inc\n")

        # The include path is relative, resolved against layer root
        errors = check_missing_includes(str(tmp_layer))
        assert len(errors) == 0

    def test_missing_require(self, tmp_layer):
        recipe_dir = tmp_layer / "recipes-test" / "test"
        recipe_dir.mkdir(parents=True)
        recipe = recipe_dir / "test_1.0.bb"
        recipe.write_text("require nonexistent.inc\n")

        errors = check_missing_includes(str(tmp_layer))
        assert any("ERROR" in e and "nonexistent.inc" in e for e in errors)

    def test_missing_include_is_warning(self, tmp_layer):
        recipe_dir = tmp_layer / "recipes-test" / "test"
        recipe_dir.mkdir(parents=True)
        recipe = recipe_dir / "test_1.0.bb"
        recipe.write_text("include optional.inc\n")

        errors = check_missing_includes(str(tmp_layer))
        assert any("WARNING" in e and "optional.inc" in e for e in errors)

    def test_variable_paths_skipped(self, tmp_layer):
        recipe_dir = tmp_layer / "recipes-test" / "test"
        recipe_dir.mkdir(parents=True)
        recipe = recipe_dir / "test_1.0.bb"
        recipe.write_text("require ${COREBASE}/meta/conf/bitbake.conf\n")

        errors = check_missing_includes(str(tmp_layer))
        assert len(errors) == 0


class TestValidateLayer:
    def test_valid_layer(self, tmp_layer_with_recipes):
        errors = validate_layer(str(tmp_layer_with_recipes))
        assert isinstance(errors, list)

    def test_empty_dir(self, tmp_path):
        errors = validate_layer(str(tmp_path))
        assert len(errors) > 0  # Should report missing conf/layer.conf
