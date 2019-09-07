The component accepts following parameters:

- login - login to GoodData, must have admin privileges,
- password - password associated with login,
- project ID - GoodData project ID,
- query - a MAQL query, which will be executed. If a row placeholder `{{ROW}}` is present in the query and a input table is specified, all of the rows in the input table are inputted into the query instead of the placeholder, one-by-one,
- custom domain (opt.) - if whitelabelled domain is used, specify it.