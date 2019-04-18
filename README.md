# Coding Pirates member mangement system.
[![CircleCI](https://circleci.com/gh/Rotendahl/forenings_medlemmer.svg?style=svg)](https://circleci.com/gh/Rotendahl/forenings_medlemmer)[![Coverage Status](https://coveralls.io/repos/github/Rotendahl/forenings_medlemmer/badge.svg?branch=master)](https://coveralls.io/github/Rotendahl/forenings_medlemmer?branch=master)
This system is used by the union [Coding Pirates][cpDK], we are a volunteer
non profit that teaches programming, 3D printing, and other IT related
activities to kids.

We use this system to mange our unions, chapters, members, activities and
volunteers.

### The system
> The system is going through a redesign and thus the code is still between
> phases and thus a bit messy.

The system is coded in [django][django], and exposes a [graphQL][graphQL]
endpoint that can be consumed by a front end, and the built in django admin
interface which is used by the administrative personal.

The system is setup using the principles of a [twelve factor app][12factor],
which makes it easy to deploy.


### Development
To get a working copy of the system up and running run the following commands in
a bash shell.
```
# git clone git@github.com:CodingPirates/forenings_medlemmer.git
# cd forenings_medlemmer
# docker-compose run --rm backend environment/reset-db.sh
# docker-compose up
```





```
./manage.py migrate
```


<!-- Links -->
[cpDK]: https://codingpirates.dk
[django]: https://www.djangoproject.com
[graphQl]: https://www.howtographql.com
[12factor]: https://12factor.net
