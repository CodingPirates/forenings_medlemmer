--Waitinglist (pr. region)
SELECT zr.region, COUNT(DISTINCT p.id) FROM members_person AS p
  INNER JOIN members_waitinglist AS wl ON wl.person_id=p.id
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode
  GROUP BY zr.region;

--Waitinglist (Total)
SELECT zr.region, COUNT(DISTINCT p.id) FROM members_person AS p
  INNER JOIN members_waitinglist AS wl ON wl.person_id=p.id
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode

--Medlemmer (pr. region)
SELECT zr.region, COUNT(DISTINCT p.id) FROM members_person AS p
  JOIN members_payment AS pay ON pay.person_id=p.id
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode
  WHERE pay.refunded_dtm IS NULL AND pay.amount_ore > 7500
  GROUP BY zr.region;

--members pr. lokalforening 2016
SELECT u.name, COUNT(DISTINCT p.id) FROM members_person AS p
  JOIN members_payment AS pay ON pay.person_id=p.id
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode
  JOIN members_activity AS a ON pay.activity_id=a.id
  JOIN members_department AS d ON a.department_id=d.id
  JOIN members_union AS u ON u.id=d.union_id
  WHERE pay.refunded_dtm IS NULL AND pay.amount_ore > 7500 AND pay.added > date('2016-01-01')
  GROUP BY u.id;

--members pr. afdeling 2016
SELECT d.name, u.name, COUNT(DISTINCT p.id) FROM members_person AS p
  JOIN members_payment AS pay ON pay.person_id=p.id
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode
  JOIN members_activity AS a ON pay.activity_id=a.id
  JOIN members_department AS d ON a.department_id=d.id
  JOIN members_union AS u ON u.id=d.union_id
  WHERE pay.refunded_dtm IS NULL AND pay.amount_ore > 7500 AND pay.added > date('2016-01-01')
  GROUP BY d.id;

--Medlemmer (pr. region) 2016
SELECT zr.region, COUNT(DISTINCT p.id) FROM members_person AS p
  JOIN members_payment AS pay ON pay.person_id=p.id
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode
  WHERE pay.refunded_dtm IS NULL AND pay.amount_ore > 7500 AND pay.added > date('2016-01-01')
  GROUP BY zr.region;

--Børn signup dato pr. region
SELECT strftime('%Y-%W', p.added) as week, COUNT(DISTINCT p.id) FROM members_person AS p
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode
  WHERE p.membertype='CH'
  GROUP BY week;

--Indkomst (pr. region)
SELECT zr.region, SUM(pay.amount_ore/100) FROM members_person AS p
  INNER JOIN members_payment AS pay ON pay.person_id=p.id
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode
  WHERE pay.refunded_dtm IS NULL
  GROUP BY zr.region;

--Activity age distribution
SELECT p.birthday FROM members_person AS p
  JOIN members_member AS m ON m.person_id=p.id
  JOIN members_activityparticipant AS ap ON ap.member_id=m.id
  WHERE ap.activity_id=160;

--Deltagerliste
SELECT p.name, f.email, ap.note FROM members_activityparticipant AS ap
JOIN members_member AS m ON ap.member_id=m.id
JOIN members_person AS p ON p.id=m.person_id
JOIN members_family AS f ON p.family_id=f.id
WHERE ap.activity_id IS 160;

--Aktivitets deltagere i en region
SELECT DISTINCT f.email, p.name FROM members_person AS p
  JOIN members_member AS m ON m.person_id=p.id
  JOIN members_activityparticipant AS ap ON ap.member_id=m.id
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode
  JOIN members_activity AS a ON a.id=ap.activity_id
  JOIN members_family AS f ON f.id=p.family_id
    WHERE zr.region IN ('DK01', 'DK02') AND a.end_date > '2017-02-21'
    AND f.dont_send_mails=0;;

--venteliste børn i en region
SELECT DISTINCT f.email, p.name FROM members_person AS p
  JOIN members_waitinglist AS w ON p.id=w.person_id 
  JOIN members_family AS f ON f.id=p.family_id
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode
    WHERE zr.region IN ('DK02')
    AND f.dont_send_mails=0;;

--medlemmer i en forening
SELECT DISTINCT f.email FROM members_person AS p
  JOIN members_member AS m ON m.person_id=p.id
  JOIN members_activityparticipant AS ap ON ap.member_id=m.id
  JOIN members_zipcoderegion AS zr ON zr.zipcode=p.zipcode
  JOIN members_activity AS a ON a.id=ap.activity_id
  JOIN members_family AS f ON f.id=p.family_id
  JOIN members_department AS d ON d.id=a.department_id
    WHERE d.union_id=2
    AND a.end_date > '2017-03-06'
    AND julianday(a.end_date) - julianday(a.start_date) > 5;

(10, 11, 21, 27, 35, 39, 40, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 84)

--Deltagere i bestemte afdelinger
SELECT DISTINCT f.email FROM members_person AS p
  JOIN members_member AS m ON m.person_id=p.id
  JOIN members_activityparticipant AS ap ON ap.member_id=m.id
  JOIN members_activity AS a ON a.id=ap.activity_id
  JOIN members_family AS f ON f.id=p.family_id
  JOIN members_department AS d ON d.id=a.department_id
    WHERE d.id IN (34, 63, 9, 69, 38)
    AND a.end_date > '2017-03-06'
    AND f.dont_send_mails=0;

--Deltagere på venteliste i bestemte afdelinger
SELECT DISTINCT f.email FROM members_person AS p
  JOIN members_family AS f ON f.id=p.family_id
  JOIN members_waitinglist AS w ON p.id=w.person_id 
    WHERE w.department_id IN (34, 63, 9, 69, 38)
    AND f.dont_send_mails=0;


