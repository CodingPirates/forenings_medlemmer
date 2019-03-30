# Coding Pirates member mangement system.
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






```
./manage.py migrate
```


<!-- Links -->
[cpDK]: https://codingpirates.dk
[django]: https://www.djangoproject.com
[graphQl]: https://www.howtographql.com
[12factor]: https://12factor.net
