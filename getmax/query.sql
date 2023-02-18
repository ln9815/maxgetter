select * from category;

INSERT INTO category(id,name,season,rootid)
  VALUES('202','xxxxx','ss2023',2)
  ON CONFLICT(id) DO UPDATE SET
    name=excluded.name,
    season=excluded.season,
	rootid=excluded.rootid