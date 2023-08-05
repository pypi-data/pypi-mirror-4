/* -*- sql -*-

   postgres specific registered procedures,
   require the plpythonu language installed

*/

CREATE OR REPLACE FUNCTION priority_sort_value(text) RETURNS int
    AS 'return {"minor": 2, "normal": 1, "important":  0}[args[0]]'
    LANGUAGE plpythonu
WITH(ISCACHABLE);;

CREATE OR REPLACE FUNCTION version_sort_value(text) RETURNS bigint AS $$
    try:
        version, _sep, revision = args[0].partition('-')
        return sum([1000000,10000,100][i]*int(v) for i, v in enumerate(version.split("."))) + int(revision or 0)
    except (ValueError, IndexError, AttributeError):
        return 0
$$ LANGUAGE plpythonu
WITH(ISCACHABLE);;
