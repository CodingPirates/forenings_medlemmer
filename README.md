# Coding Pirates member mangement system.
![CircleCI branch](https://img.shields.io/circleci/project/github/CodingPirates/forenings_medlemmer/master.svg?style=for-the-badge)![Coveralls github branch](https://img.shields.io/coveralls/github/CodingPirates/forenings_medlemmer/master.svg?style=for-the-badge)![Code style: black](https://img.shields.io/badge/CODE%20STYLE-Black-black.svg?style=for-the-badge)


This system is used by the union [Coding Pirates][cpDK], we are a volunteer
non profit that teaches programming, 3D printing, and other IT related
activities to kids.

We use this system to manage our unions, chapters, members, activities and
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
For more info, see our [wiki][wiki] or ask on [Slack][slack]

<!-- Links -->
[cpDK]: https://codingpirates.dk
[django]: https://www.djangoproject.com
[graphQl]: https://www.howtographql.com
[12factor]: https://12factor.net
[wiki]: https://github.com/CodingPirates/forenings_medlemmer/wiki
[slack]: https://slackinvite.codingpirates.dk/
