#Waitinglist (pr. region)
SELECT zr.region, COUNT(DISTINCT p.id) FROM members_person AS p
  INNER JOIN members_waitinglist AS wl ON wl.person_id=p.id
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode
  GROUP BY zr.region;

#Waitinglist (Total)
SELECT zr.region, COUNT(DISTINCT p.id) FROM members_person AS p
  INNER JOIN members_waitinglist AS wl ON wl.person_id=p.id
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode

# Medlemmer (pr. region)
SELECT zr.region, COUNT(DISTINCT p.id) FROM members_person AS p
  JOIN members_payment AS pay ON pay.person_id=p.id
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode
  WHERE pay.refunded_dtm IS NULL AND pay.amount_ore > 7500
  GROUP BY zr.region;

# Medlemmer (pr. region) 2016
SELECT zr.region, COUNT(DISTINCT p.id) FROM members_person AS p
  JOIN members_payment AS pay ON pay.person_id=p.id
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode
  WHERE pay.refunded_dtm IS NULL AND pay.amount_ore > 7500 AND pay.added > date('2016-01-01')
  GROUP BY zr.region;

# Børn signup dato pr. region
SELECT strftime('%Y-%W', p.added) as week, COUNT(DISTINCT p.id) FROM members_person AS p
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode
  WHERE p.membertype='CH'
  GROUP BY week;

# Indkomst (pr. region)
SELECT zr.region, SUM(pay.amount_ore/100) FROM members_person AS p
  INNER JOIN members_payment AS pay ON pay.person_id=p.id
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode
  WHERE pay.refunded_dtm IS NULL
  GROUP BY zr.region;
