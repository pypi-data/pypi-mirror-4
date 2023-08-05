"PyXB" does not handle "xs:redefine" used by the offical authentication context
schemata.

Therefore, I have manually changed the schema definitions to avoid
"xs:redefine". Modification has been by textually including the
base schema and then changing the redefined elements in the copy.
As a consequence, the modified schemas should be functionally equivalent
to the original one (unless I made an error) but are far less readable.
