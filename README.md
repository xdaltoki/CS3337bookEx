# CS3337bookEx — Team Workflow Guide

Django 6.0.1 book-exchange app for CSULA CS 3337. This README is the **operating manual for the team**: how to set up, what to do when you change the database schema, how to pull changes cleanly, and how to prep for a demo. Read sections you need — they're independent.

---

## 1. First-time setup (new teammate, fresh clone)

1. **Install Anaconda** (if you haven't). Any recent Anaconda release with Python ≥ 3.12 works — Django 6.0.1 requires 3.12+.
2. **Clone the repo** and `cd` into it.
3. Open **Anaconda Prompt** (Start Menu → "Anaconda Prompt"). Do **not** use plain PowerShell — on most machines it resolves `python` to a system Python that doesn't have Django installed, and you'll waste an hour debugging why.
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Build your local database from the migration files:
   ```
   python manage.py migrate
   ```
   This creates `db.sqlite3` from scratch. If one already exists from an older clone, see §4 for conflict recovery.
6. Create a superuser so you can log into `/admin/`:
   ```
   python manage.py createsuperuser
   ```
7. Start the dev server:
   ```
   python manage.py runserver
   ```
   Visit http://127.0.0.1:8000/ — you should see the site. The sidebar will be empty until you add rows to **Main menus** in `/admin/`.

---

## 2. The rule: whenever you change `models.py`, commit migration files with it

This is the single most important habit on this project. **Every time** anyone edits [bookMng/models.py](bookMng/models.py) — adding a model, adding a field, renaming anything, changing a constraint — they must:

### Step-by-step (the author's side)

1. Edit `bookMng/models.py`.
2. In Anaconda Prompt, from the repo root, run:
   ```
   python manage.py makemigrations bookMng
   ```
   Django prints something like:
   ```
   Migrations for 'bookMng':
     bookMng\migrations\0005_yourfeature.py
       + Add field foo to bar
   ```
3. Apply it to your own DB to verify it works:
   ```
   python manage.py migrate
   ```
4. Run the dev server and manually click through the feature to confirm it's not broken.
5. **Commit both files together** — the `models.py` edit **and** the new file under `bookMng/migrations/`. Run `git status` before committing; if you don't see a new migration file there, something is wrong — stop and ask.

   ```
   git add bookMng/models.py bookMng/migrations/0005_yourfeature.py
   git commit -m "Add Foo feature"
   git push
   ```

**If you forget to commit the migration file**, the rest of the team will pull your `models.py`, Django will see a model it doesn't have a migration for, and the next `makemigrations` will try to generate a big catch-all migration that conflicts with your DB. That's literally what happened on this repo with the `Rating` model, and it took an hour to untangle. The migration file is tiny (usually 20–40 lines) but it is **not optional** — it is the record of how the schema changes over time.

### Step-by-step (everyone else's side, after pulling)

When you `git pull` and see new files under `bookMng/migrations/`:

```
python manage.py migrate
```

That's it. Django reads the new migration files, figures out which ones haven't run on your local DB yet, and applies them in order. Then restart your runserver.

---

## 3. Files that must be in the commit when you change schema

| File | When |
|---|---|
| `bookMng/models.py` | The edit that started everything. |
| `bookMng/migrations/XXXX_something.py` | **The new file** `makemigrations` generated. Required. |
| `bookMng/forms.py` | If you added/renamed a form or changed fields the form exposes. |
| `bookMng/views.py` | If the new model gets queried or written by any view. |
| `bookMng/urls.py` | If you added a new URL for the feature. |
| `bookEx/templates/bookMng/*.html` | If the UI changed. |

You do **not** need to include `db.sqlite3` in the commit — in fact don't (see §6). `manage.py` itself almost never changes; leave it alone.

---

## 4. Pulling changes when someone else changed models

The normal flow after `git pull`:

```
pip install -r requirements.txt     # in case requirements.txt changed
python manage.py migrate            # apply any new migrations
python manage.py runserver
```

### Troubleshooting: "table already exists" after pulling

If you see an error like:
```
django.db.utils.OperationalError: table "bookMng_rating" already exists
```
…it means your local `db.sqlite3` has a table the migration is trying to create. This is the exact bug the retroactive [0003_rating_and_average_rating.py](bookMng/migrations/0003_rating_and_average_rating.py) migration exists to document. Two fixes:

**Option A (keeps your local data):** fake-apply the offending migration once:
```
python manage.py migrate --fake bookMng 0003
python manage.py migrate
```
`--fake` tells Django "mark this migration as already applied, without running its SQL." Use only when you're certain the schema already matches.

**Option B (nukes your local data, clean slate):** delete your local DB and rebuild from migrations:
```
# Windows
del db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```
You'll lose any books, users, and ratings you had locally. Usually fine during development.

---

## 5. Before a live demo off `master`

Do this on your own machine (or the demo laptop) the morning of the demo — **don't wait until 30 seconds before you present.**

1. Make sure everything is merged to master on GitHub. No PRs still open for things you plan to show.
2. Fresh terminal, from the repo root:
   ```
   git checkout master
   git pull origin master
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py check
   python manage.py runserver
   ```
3. In a browser, run through the exact demo script — every click, every form, every page — while watching the server terminal for red tracebacks. Tracebacks during a demo look much worse than a calm "let me show you this other feature."
4. Log into `/admin/` and confirm the sidebar menu entries exist (they live in the `MainMenu` table and often get lost when DBs are rebuilt). Add them if missing:
   - Home → `/`
   - Display Books → `/displaybooks`
   - Post Book → `/postbook`
   - My Books → `/mybooks`
5. Add at least two test books with pictures and a few test ratings/comments so the demo pages aren't empty.
6. Keep the Anaconda Prompt running `runserver` visible off-screen (or on a second monitor) — if something breaks during the demo, the traceback there tells you what to check.
7. Zoom the browser to ~125% — text is easier to read from a projector.

---

## 6. Why `db.sqlite3` shouldn't be committed going forward

Right now `db.sqlite3` **is** tracked in git, which is why pulling a teammate's commit can overwrite your local data and why schema drift keeps causing `table already exists` errors. The standard Django practice is to treat the DB as disposable local state that each developer rebuilds from migrations. `db.sqlite3` is already listed in [.gitignore](.gitignore), but because git already tracks it, that line does nothing until someone removes it from tracking.

**One-time cleanup (do this together as a team, not solo):**

1. Everyone commits and pushes whatever they currently have.
2. One person runs:
   ```
   git rm --cached db.sqlite3
   git commit -m "Stop tracking db.sqlite3; each dev builds their own"
   git push
   ```
   (The `--cached` flag removes it from git without deleting the file from disk.)
3. Everyone else pulls. Their local `db.sqlite3` is untouched; git just stops caring about it.
4. From then on, changes to the DB don't show up in `git status` and don't end up in commits.

**Caveat:** if your course grader/instructor expects to clone the repo and see a working site with sample data without running `migrate`, skip this step for now and keep committing `db.sqlite3` — follow whatever your instructor's submission convention says. For between-team work, the above cleanup is worth it.

---

## 7. Common commands cheat sheet

Run all of these from the repo root, in Anaconda Prompt:

| Command | What it does |
|---|---|
| `python manage.py runserver` | Start the dev server at http://127.0.0.1:8000/ |
| `python manage.py makemigrations bookMng` | Generate migration file after editing `models.py` |
| `python manage.py migrate` | Apply pending migrations to your local DB |
| `python manage.py migrate --fake bookMng XXXX` | Mark migration `XXXX` as applied without running it (recovery only) |
| `python manage.py createsuperuser` | Create an admin login for `/admin/` |
| `python manage.py showmigrations bookMng` | List migrations and whether each has been applied |
| `python manage.py check` | Run Django's static checks; should print "no issues" |
| `python manage.py test bookMng` | Run app tests |

PyCharm users: you can run the server with the **Run ▶** button once you've set up a Python run configuration (Script path = `manage.py`, Parameters = `runserver 127.0.0.1:8000`, Interpreter = your conda base env).
