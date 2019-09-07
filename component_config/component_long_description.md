# MAQL Executioner for GoodData

MAQL is an analytical language used in GoodData to perform all analytical tasks. This component allows to execute a MAQL query against a GoodData project and perform various integration. For MAQL reference, refer to [MAQL documentation](https://help.gooddata.com/doc/en/reporting-and-dashboards/maql-analytical-query-language).

Further reference:
- [list datasets by project](https://help.gooddata.com/display/API/API+Reference#/reference/data-integration/list-datasets-by-project/list-datasets-by-project),
- [acquiring object identifiers](https://help.gooddata.com/doc/en/project-and-user-administration/administering-projects-and-project-objects/acquiring-object-identifiers-for-project-metadata)
- [deleting records from dataset](https://help.gooddata.com/doc/en/building-on-gooddata-platform/data-preparation-and-distribution/additional-data-load-reference/data-load-tutorials/deleting-records-from-datasets)

### Use cases

The component can be used for automated deletion of records from certain datasets.

#### Date based deletion

To delete records from dataset based on date value, you can specify an input table with one row and column, which would contain the date value (e.g. `2017-01-01`) and then specify the following query:

```
DELETE FROM {attr.dataset.factsof} WHERE {datetransportbegin.keboola.date.yyyymmdd} < "{{ROW}}";
```

The `{{ROW}}` would be automatically replaced by value from the input table.

#### Attribute value based deletion

To delete records matching certain criteria, conditions can be specified in the input table. A condition can be anything, a list of values or a single value.

For the query:

```
DELETE FROM {attr.dataset.factsof} WHERE {label.dataset.attribute} IN {{ROW}}
```

and specify values in the input table, for example: `("1234532", "attributeValue")` and in the next row `("nextValue")`. All of the values specified in the input table will be inputed instead of `{{ROW}}` and executed.