
Yes — if you already know Express.js + Node + MongoDB/Mongoose, this Flask project becomes much easier. Think of it as almost the same architecture with different names.

The fastest mapping

Flask project you showed	Express / Node equivalent	What it does
server.py	server.js / app.js	Starts/configures the application
routes/	routes/	Maps URL → handler/controller
resources/	controllers/	Handles HTTP request/response + business logic
repositories/	repositories/, services/, or DB layer	Executes DB queries
models/	models/ / Mongoose schemas	Describes database entities
db.py	db.js, mongoose.connect()	DB connection/session
client/	services/ / clients/	Calls external APIs
constants/	constants/, enums/	Fixed values/statuses
util/	utils/	Helpers
config.py	config.js	Configuration
.env	.env	Environment variables
swagger/	Swagger/OpenAPI YAML	API documentation
test/	tests/	Tests
decorators like @required_authentication()	Express middleware	Auth/authorization
@parse_params(...)	validation middleware / req.body schema	Parses/validates request payload

⸻

1. Express mental model

In Express you may be used to something like:

src/
├── routes/
│   └── initiative.routes.js
├── controllers/
│   └── initiative.controller.js
├── services/
│   └── initiative.service.js
├── models/
│   └── initiative.model.js
├── middleware/
├── config/
└── app.js

Your Flask repo is approximately:

src/
├── routes/
├── resources/
│   └── initiative/
│       └── initiative.py
├── repositories/
│   └── initiative.py
├── models/
│   └── initiative.py
├── client/
├── constants/
├── util/
├── config.py
├── db.py
└── server.py

So mentally rename:

Resource ≈ Controller
Repository ≈ DB Service / DAO
Model ≈ Mongoose Model

That alone gets you about 80% there.

⸻

2. Express Controller vs Flask Resource

In Express you might write:

router.get('/initiatives/:id', getInitiative);

Then:

const getInitiative = async (req, res) => {
  const initiative = await Initiative.findById(req.params.id);
  res.json(initiative);
};

In your Flask project you have something like:

class InitiativeByIdResource(Resource):
    def get(user, id):
        initiative = InitiativeRepository.get(id).to_json()
        return initiative

Same idea:

Express                          Flask
req.params.id              →     id
controller function        →     Resource.get()
res.json(...)              →     return ...
Mongoose query             →     Repository method

⸻

3. Your Resource is basically your Express controller

This:

class InitiativeByIdResource(Resource):

is similar to having:

export const getInitiative = ...
export const updateInitiative = ...

Inside the Flask class:

def get(...)
def patch(...)

is basically:

GET handler
PATCH handler

So:

Flask Resource
class InitiativeByIdResource:
    get()
    patch()

≈

Express Controller
getInitiative()
patchInitiative()

⸻

4. Repository is where your project differs slightly

In a small Express/Mongoose application, you might directly do this in the controller:

const initiative = await Initiative.findById(id);

But this Flask project doesn’t want the controller talking directly to DB.

Instead:

InitiativeRepository.get(id)

Then inside repository:

def get(initiative_id):
    initiative = db.session.scalars(
        select(Initiative).where(
            Initiative.id == initiative_id
        )
    )

Equivalent Node architecture would be:

// initiative.repository.js
export async function get(id) {
  return Initiative.findById(id);
}

Controller:

const initiative = await InitiativeRepository.get(id);

So this project has an explicit DB layer:

Controller
    ↓
Repository
    ↓
Model

Instead of:

Controller
    ↓
Mongoose

⸻

5. SQLAlchemy Model vs Mongoose Model

This is probably the biggest conceptual difference for you.

Mongo/Mongoose

You might know:

const initiativeSchema = new mongoose.Schema({
  name: String,
  fees_desc: String,
  aum_expected: String
});
const Initiative = mongoose.model(
  'Initiative',
  initiativeSchema
);

You store a document approximately like:

{
  "_id": "...",
  "name": "Fund initiative",
  "fees_desc": "1.2%",
  "aum_expected": "100M"
}

Flask + SQLAlchemy

You’ll find something conceptually like:

class Initiative(db.Model):
    id = db.Column(...)
    name = db.Column(...)
    fees_desc = db.Column(...)
    aum_expected = db.Column(...)

This represents a SQL table:

initiative
------------------------------------------------
id | name | fees_desc | aum_expected | ...

So:

Mongoose Schema
        ≈
SQLAlchemy Model

But database philosophy differs:

MongoDB
document-oriented
{
  teams: [...],
  tasks: [...]
}

versus relational SQL:

initiative
initiative_task
initiative_team_relationship
initiative_committee_date
...

And your repo clearly has many related models/repos:

initiative
initiative_task
initiative_team_relationship
initiative_committee_date
initiative_timeline_status
...

That’s very typical relational architecture.

⸻

6. Mongoose query → SQLAlchemy query

You know:

Initiative.findById(id)

Flask project:

select(Initiative).where(
    Initiative.id == id
)

You know:

Initiative.find({
  createdBy: { $in: userIds }
})

Your Flask repo has approximately:

Initiative.query.filter(
    Initiative.created_by_id.in_(created_by_ids)
)

You know:

Initiative.find({
  _id: { $in: initiativeIds }
})

Flask:

Initiative.query.filter(
    Initiative.id.in_(initiative_ids)
)

So mentally:

Mongoose `.find()`
≈
SQLAlchemy `select()` / `.query.filter()`

⸻

7. db.session compared to Mongo

This is one important new thing.

You saw:

db.session

With Mongoose you often simply:

await initiative.save();

SQLAlchemy generally has a database session:

db.session.add(obj)
db.session.commit()

Think:

db.session
=
current unit of database work

It tracks objects and transactions.

Conceptually:

Mongo/Mongoose:
doc.save()

versus:

SQLAlchemy:
db.session.add(doc)
db.session.commit()

⸻

8. POST comparison

Your Flask Resource has:

def post(
    user,
    name,
    template_id,
    summary,
    product_type,
    ...
):

Then:

InitiativeRepository.create(
    name=name,
    template_id=template_id,
    summary=summary,
    ...
)

Express version:

const createInitiative = async (req, res) => {
  const {
    name,
    template_id,
    summary,
    product_type
  } = req.body;
  const initiative =
    await InitiativeRepository.create({
      name,
      template_id,
      summary,
      product_type
    });
  res.json(initiative);
};

Almost identical conceptually.

⸻

9. What is @parse_params(...)?

You saw:

@parse_params(
    Argument("name", type=str, location="json"),
    Argument("summary", type=str, location="json"),
    Argument("fees_desc", type=str, location="json"),
)

In Express you might do:

const {
  name,
  summary,
  fees_desc
} = req.body;

Or with Joi/Zod:

const schema = z.object({
  name: z.string(),
  summary: z.string(),
  fees_desc: z.string()
});

So:

@parse_params
≈
req.body parsing + validation middleware

It converts JSON request body into Python arguments.

⸻

10. What is **kwargs compared to JavaScript?

This:

def patch(user, id, **kwargs):

is extremely similar to JavaScript’s object/rest behavior.

Imagine request body:

{
  "fees_desc": "New fees",
  "aum_expected": "100M"
}

Python:

kwargs = {
    "fees_desc": "New fees",
    "aum_expected": "100M"
}

Then:

InitiativeRepository.modify(
    id,
    **kwargs
)

is conceptually:

InitiativeRepository.modify(id, {
  ...req.body
});

So:

Python **kwargs
≈
JavaScript ...object

Very useful correspondence.

⸻

11. Authentication decorators = Express middleware

You saw:

@required_authentication()
@authorized_plm_roles([...])
def patch(...):

That’s basically:

router.patch(
  '/initiatives/:id',
  requiredAuthentication,
  authorizedRoles(...),
  updateInitiative
);

Flask:

@required_authentication
          ↓
@authorized_plm_roles
          ↓
patch()

Express:

router.patch(
  auth,
  authorization,
  controller
)

Same pattern, different syntax.

⸻

12. client/plm = Axios service

You saw:

from client.plm import (
    get_teams_by_team_id,
    get_users_by_user_id
)

This is probably equivalent to your Node code:

import axios from 'axios';
export async function getTeam(id) {
  return axios.get(`${PLM_URL}/teams/${id}`);
}

So:

client/

means:

This backend is acting as a client of another backend.

Architecture:

React
  ↓
FLOWR Flask API
  ↓
PLM API

Equivalent Express folder often called:

services/
clients/
integrations/
api/

⸻

13. constants/

Exactly the same as Node.

Python:

class TaskStatus:
    DONE = "DONE"
    CANCELED = "CANCELED"

Node:

export const TaskStatus = {
  DONE: 'DONE',
  CANCELED: 'CANCELED'
};

You also saw:

InitiativeRoleEnum.INITIATIVE_OWNER

Equivalent TS:

enum InitiativeRole {
  INITIATIVE_OWNER = 'INITIATIVE_OWNER'
}

⸻

14. swagger/

Same concept as Express Swagger.

You have:

@swag_from(
  "../../../swagger/initiatives/GET_id.yml"
)

Equivalent Node:

/**
 * @swagger
 * /initiatives/{id}:
 *   get:
 *     ...
 */

or separate:

swagger/
openapi.yaml

It’s just API documentation/schema.

⸻

15. .wrap.py / decorators concept

This project uses many Python decorators:

@staticmethod
@required_authentication()
@authorized_plm_roles(...)
@parse_params(...)
@swag_from(...)

If you’re from Express, mentally read:

@something
def patch():

as:

something(
  patch
)

It’s wrapping the function.

Very similar to middleware/HOCs conceptually.

⸻

16. SessionCriticalActionManager

This:

with SessionCriticalActionManager(...):

is Python’s context-manager pattern.

Comparable idea in JS:

try {
  await session.startTransaction();
  // operations
  await session.commitTransaction();
} catch (e) {
  await session.abortTransaction();
  throw e;
}

I wouldn’t say it definitely does exactly that until we open its implementation, but structurally:

with Something:
    ...

means:

setup something → execute block → cleanup afterward, including on error.

⸻

17. Your exact frontend → backend example

You just worked on:

<SmartField
  name="feesDesc"
  displaySnakeKey="fees_desc"
/>

Frontend sends something approximately:

{
  fees_desc: value
}

Then Flask:

Argument(
  "fees_desc",
  type=str,
  location="json"
)

Then:

def patch(user, id, **kwargs):

So:

kwargs["fees_desc"]

then:

InitiativeRepository.modify(
    id,
    **kwargs
)

then SQLAlchemy Model:

Initiative.fees_desc

then database column:

initiative.fees_desc

Using Node/Mongo language:

React
 ↓
axios.patch()
 ↓
Express route
 ↓
controller
 ↓
req.body.fees_desc
 ↓
repository
 ↓
Initiative.findByIdAndUpdate(...)
 ↓
MongoDB

Flask equivalent:

React
 ↓
PATCH
 ↓
Resource.patch()
 ↓
kwargs["fees_desc"]
 ↓
InitiativeRepository.modify()
 ↓
SQLAlchemy Initiative
 ↓
SQL DB

⸻

The one cheat sheet I’d keep in your head

NODE / EXPRESS / MONGO             THIS FLASK PROJECT
────────────────────────────────────────────────────
server.js                   ↔      server.py
app.js                      ↔      server.py/config.py
routes/                     ↔      routes/
controllers/                ↔      resources/
service/repository          ↔      repositories/
Mongoose Model              ↔      SQLAlchemy Model
mongoose                    ↔      SQLAlchemy
mongoose.connect()          ↔      db.py
req.body                    ↔      parsed params / kwargs
req.params.id               ↔      id
res.json(data)              ↔      return data
.findById(id)               ↔      Repository.get(id)
.find(...)                  ↔      select()/query.filter()
.findByIdAndUpdate()        ↔      Repository.modify()
.create()                   ↔      Repository.create()
.populate()                 ↔      relationships / joins /
                                extra repository/client calls
middleware                  ↔      decorators
Joi / Zod                   ↔      Argument + parse_params
Axios to another API        ↔      client/
enums/constants             ↔      constants/
Swagger                     ↔      swagger/
Mongo document              ↔      SQL row/model object

And the biggest difference you need to adapt to is this:

Your familiar Express + Mongo:
Route
 → Controller
 → Mongoose Model
 → Mongo

This repo deliberately adds one layer:

Flask:
Route
 → Resource
 → Repository
 → SQLAlchemy Model
 → SQL database

So whenever you’re lost in this backend, translate Resource = controller and Repository = the place where you’d normally write your Mongoose query. That will make the structure feel very familiar.