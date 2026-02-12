(function () {
    "use strict";

    function isConfigEmpty(value) {
        // Treat empty string, "{}", or whitespace-only as "empty"
        if (!value) return true;
        try {
            var parsed = JSON.parse(value);
            return Object.keys(parsed).length === 0;
        } catch (e) {
            return !value.trim() || value.trim() === "{}";
        }
    }

    function applySchemaTemplate() {
        var typeSelect = document.getElementById("id_integration_type");
        var configField = document.getElementById("id_config");
        if (!typeSelect || !configField) return;

        var schemas = window._configSchemas || {};

        typeSelect.addEventListener("change", function () {
            var selectedType = typeSelect.value;
            if (!selectedType) return;

            // Only auto-fill when the config is empty (don't overwrite user edits)
            if (!isConfigEmpty(configField.value)) return;

            var schema = schemas[selectedType];
            if (schema && Object.keys(schema).length > 0) {
                configField.value = JSON.stringify(schema, null, 2);
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", applySchemaTemplate);
    } else {
        applySchemaTemplate();
    }
})();

