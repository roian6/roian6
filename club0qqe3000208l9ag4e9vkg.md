---
title: "백준 스트릭 세이버 제작기 🪄"
seoTitle: "백준 스트릭 세이버 제작기 🪄"
seoDescription: "입대 후 백준 스트릭을 유지하기 위해, Playwright와 Github Actions를 활용한 자동 제출 프로그램을 제작한 과정에 대해 소개합니다."
datePublished: Thu Mar 28 2024 09:14:51 GMT+0000 (Coordinated Universal Time)
cuid: club0qqe3000208l9ag4e9vkg
slug: boj-streak-saver
cover: https://cdn.hashnode.com/res/hashnode/image/upload/v1711612014906/01c1d792-702c-454d-8149-db8fec260e2b.png
tags: python, captcha, github-actions-1, playwright

---

## ☠️ 개발 배경

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1711612034002/da20e60a-50d7-4833-a888-7fd612aac58b.png align="center")

나는 수능 이후부터 지금까지 백준 스트릭을 2년 이상 유지하고 있다. 물론 처음에는 알고리즘 실력을 쌓겠다는 목표로 시작했으나, 지금은 본말이 전도되어 스트릭을 쌓는 것 자체에 더 재미를 느끼고 있다. (당연히 실력은 제자리걸음이다.)

여행을 가서도 백준을 풀고 심지어 휴대폰으로 답안을 제출하는 등 스트릭 유지를 위해 갖은 수를 썼지만, 그럼에도 어찌할 수 없는 것이 있었으니 바로 [군대](https://roian6.hashnode.dev/army-tiger)다. 훈련소에서 매일 백준을 풀 수는 없지 않은가?

따라서 내가 물리적으로 문제를 풀 수 없는 기간에도 스트릭을 유지할 수 있게 도와주는 프로그램을 만들기로 결심했다. 물론 알고리즘 실력에는 하등 도움이 안 되는 사짜같은 발상이지만 어쩌겠는가? 솔직히 800 스트릭은 좀 아깝다. 🤔

## ⚙️ 설계 및 사용 기술

사용 시나리오는 대략 아래와 같이 구상했다.

1. 부계정으로 문제를 풀어 정답 코드를 다수 확보한다.
    
2. 정답 코드들을 프로그램 안에 넣어 둔다.
    
3. 프로그램이 매일 특정 시간에 백준에 문제를 하나 제출한다.
    
4. 제출 결과에 대한 알림을 슬랙으로 받는다.
    

개발 언어는 익숙한 **파이썬**으로 정했다. 웹 자동화 프레임워크는 원래 Selenium을 사용했었는데, 요새는 마이크로소프트에서 만든 [Playwright](https://playwright.dev/)를 많이 쓰는 것 같아 이번 기회에 써보기로 했다.

프로그램은 [Github Actions](https://github.com/features/actions) 위에서 돌리기로 했다. 세팅이 간편하기도 하고 무료이기 때문이다.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1711609158282/777a2b32-2940-4b16-a352-3fe936f4530d.png align="left")

최종 프로젝트 구조는 위와 같다. Github Actions에서 실행할 내용을 담은 `main.yml`, 정답 소스들을 넣어둘 `answers` 폴더, 실제 프로그램을 작성할 `program.py`와 설치해야 할 파이썬 패키지들을 나열한 `requirements.txt` 파일로 구성되어 있다.

## 💻 개발 과정

*실제 개발 순서와는 다소 차이가 있다.*

### 파이썬 프로그램 (program.py)

1. 먼저 브라우저를 열고 백준 사이트에 진입하여 로그인을 해야 한다. Playwright를 이용해 브라우저를 대강 세팅하고, 로그인 페이지로 이동시켰다.
    

```python
page.goto("https://www.acmicpc.net/login")
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1711613178535/20427e42-1b0e-4b6a-93a4-2d2193182079.png align="center")

---

2. 아이디와 패스워드를 입력하고 로그인 버튼을 누른다.
    

```python
page.fill('[name=login_user_id]', USER_ID)
page.fill('[name=login_password]', USER_PW)
page.click('[id=submit_button]')
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1711613388888/e5e4e299-6c92-45a2-b894-6769a099fa7d.png align="center")

여기서 문제가 생겼다. 백준 로그인 페이지에 캡차(reCAPTCHA v2 Invisible)가 적용되어 있어 간헐적으로 로그인에 실패하는 상황이 발생했다.

프로그램 실행 실패는 곧 스트릭 깨짐으로 이어지기 때문에 캡차는 반드시 해결해야 할 과제가 되었다.

---

3. 캡차를 우회할 방법을 찾다 [playwright\_recaptcha](https://pypi.org/project/playwright-recaptcha/) 패키지를 발견했다. 캡차의 음성으로 듣기 옵션을 통해 STT로 해석하거나, [CapSolver](https://www.capsolver.com/)가 제공하는 이미지 식별 기능을 통해 캡차를 해독하는 작업이 가능하더라.
    

```python
with recaptchav2.SyncSolver(page) as solver:
    solver.solve_recaptcha(wait=True, wait_timeout=10)
```

여기서 시행착오과 시간 소요가 제일 많았다. 먼저 해당 패키지는 아직 한국어를 지원하지 않는데, 백준 사이트에서 기본적으로 한글 캡차가 보여지므로 브라우저의 `locale`을 영어권으로 변경해야 했다.

```python
context = browser.new_context(locale='en-US')
```

또한 프로그램을 headless 브라우저(화면에 보이지 않고 백그라운드에서 돌아가는 브라우저)로 실행해야 하는데, 크롬 브라우저를 headless 모드로 사용할 경우 캡차에서 무한로딩이 발생하는 문제가 있었다. 따라서 브라우저를 Firefox로 변경했다.

```python
browser = playwright.firefox.launch(headless=True)
```

마지막으로 reCAPTCHA의 음성으로 듣기 옵션은 일정 횟수 이상 사용하면 부적절한 요청으로 판별되어 차단당하게 된다. 따라서 해당 옵션을 시도한 뒤 실패할 경우 이미지 식별로 재시도하는 로직을 추가해야 했다.

```python
def login(page: Page, is_first: bool):
    <submit login info...>
    try:
        if is_first:
            with recaptchav2.SyncSolver(page) as solver:
                solver.solve_recaptcha(wait=True, wait_timeout=10)
        else:
            with recaptchav2.SyncSolver(page, capsolver_api_key=CAPSOLVER_KEY) as solver:
                solver.solve_recaptcha(wait=True, wait_timeout=10, image_challenge=True)
    except RecaptchaRateLimitError as e:
        if is_first:
            login(page, is_first=False)
        else:
            raise e
```

[CapSolver](https://www.capsolver.com/)를 통한 이미지 식별 기능은 유료이며 API 키가 필요하나, 가격은 요청 1000회 당 400~800원 꼴로 매우 저렴하며 가입 시 1$를 지급하므로 무료 범위 내에서 문제 없이 사용할 수 있다.

이렇게 캡차 문제를 해결할 수 있었다. 역시 기술로 안 되는 건 없구나 싶더라.

---

4. 정답 소스 목록에서 하나를 임의로 선택하여 가져온다.
    

```python
answer_files = os.listdir('answers')
if not answer_files:
    raise NoAnswerError(message='남은 답안이 없어 제출에 실패했습니다.')

answer_file = str(random.choice(answer_files))
problem_number = answer_file[:answer_file.find('.')]
answer_code = open('answers/' + answer_file, 'r').read()
```

---

5. 제출 창으로 이동해 문제를 제출한다.
    

```python
page.goto(f'https://www.acmicpc.net/submit/{problem_number}')
page.evaluate('code => document.querySelector(".CodeMirror").CodeMirror.setValue(code)', answer_code)
page.click('[id=submit_button]')
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1711615536295/408950d3-0807-4c3b-be81-08cd524a95c9.png align="center")

6. 채점 결과를 기다린다.
    

```python
result_node = page.locator('#status-table tbody tr:first-child .result-text:not(.result-wait, .result-compile, .result-judging)')
result_text = result_node.text_content()
result_class = str(result_node.evaluate("node => node.className"))
```

채점 결과 테이블에서 첫 번째에 있는 결과가 채점 기다리는 중, 채점 중 등의 로딩 상태가 아니게 될 때 까지 기다렸다가 결과값을 받아오도록 했다. (Playwright는 아이템을 탐색하거나 클릭하는 등의 작업을 실행하면 그 아이템이 화면에 나타날 때까지 자동으로 기다려 준다.)

---

7. 채점 결과와 남은 문제를 슬랙으로 전송하고, 제출한 문제 파일은 삭제한다.
    

```python
        is_ac = 'ac' in result_class
        slack_message += 'AC를 받았습니다!' if is_ac else 'AC를 받지 못했습니다.'

        os.remove('answers/' + answer_file)
        answer_left = len(answer_files) - 1

        slack_message += f' \n채점 결과: {result_text} \n남은 문제는 {answer_left}개입니다.'

        if answer_left:
            hook_slack(slack_message, important=not is_ac)
        else:
            hook_slack(slack_message + '\n\n남은 문제가 없습니다!', important=True)
```

만약 폴더에 남은 문제가 없거나, AC를 받지 못하는 등 스트릭에 영향을 줄 수 있는 문제가 발생할 경우 슬랙 메시지 앞에 \[중요\] 문구를 붙이도록 설정해 두었다.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1711616467505/502ef404-1d29-4c99-869b-dbb9317319a2.png align="center")

이렇게 코드 자동 제출 기능의 구현을 완료했다.

---

전체 코드는 아래와 같다.

```python
import os
import sys
import random
import traceback
from datetime import datetime, timedelta
from requests import post, Response
from playwright.sync_api import BrowserContext, sync_playwright, Page
from playwright_recaptcha import recaptchav2, RecaptchaNotFoundError, RecaptchaRateLimitError

USER_ID = sys.argv[1]
USER_PW = sys.argv[2]

SLACK_API_URL = "https://slack.com/api/chat.postMessage"

SLACK_BOT_TOKEN = sys.argv[3]
SLACK_CHANNEL = sys.argv[4]

CAPSOLVER_KEY = sys.argv[5]


class NoAnswerError(Exception):
    def __init__(self, message="An error occurred", code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} - Code: {self.code}" if self.code else self.message


def __get_now() -> datetime:
    now_utc = datetime.utcnow()
    korea_timezone = timedelta(hours=9)
    now_korea = now_utc + korea_timezone
    return now_korea


def hook_slack(message: str, important=False) -> Response:
    korea_time_str = __get_now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "text": f"> {'[중요] ' if important else ''}{korea_time_str} *백준 스트릭 봇* \n{message}",
        "channel": SLACK_CHANNEL,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
    }
    print(message)
    res = post(SLACK_API_URL, json=payload, headers=headers)
    return res


def login(page: Page, is_first: bool):
    print('navigating to login page...')
    if is_first:
        print('(might take long, due to browser setup)')
    page.goto("https://www.acmicpc.net/login")
    print('success!\n')

    print('submitting login info...')
    page.fill('[name=login_user_id]', USER_ID)
    page.fill('[name=login_password]', USER_PW)
    page.click('[id=submit_button]')
    print('success!\n')

    try:
        if is_first:
            with recaptchav2.SyncSolver(page) as solver:
                print('trying captcha...')
                solver.solve_recaptcha(wait=True, wait_timeout=10)
        else:
            with recaptchav2.SyncSolver(page, capsolver_api_key=CAPSOLVER_KEY) as solver:
                print('retrying captcha with image...')
                solver.solve_recaptcha(wait=True, wait_timeout=10, image_challenge=True)
        print('success!\n')
    except RecaptchaNotFoundError:
        print('success! no captcha found.\n')
    except RecaptchaRateLimitError as e:
        if is_first:
            print('rate limit, retry with image.\n')
            login(page, is_first=False)
        else:
            print('retry also failed.\n')
            raise e
    except Exception as e:
        if 'detached' in str(e):
            print('success! no captcha found. (detached)\n')
        else:
            raise e


def run(ctx: BrowserContext) -> None:
    try:
        print('loading answers...')
        answer_files = os.listdir('answers')
        if not answer_files:
            print('no answer left.\n')
            raise NoAnswerError(message='남은 답안이 없어 제출에 실패했습니다.')

        answer_file = str(random.choice(answer_files))
        problem_number = answer_file[:answer_file.find('.')]
        answer_code = open('answers/' + answer_file, 'r').read()
        print(f'success! {answer_file} selected.\n')

        slack_message = f'제출 문제는 https://www.acmicpc.net/problem/{problem_number} 입니다.\n\n'

        page = ctx.new_page()

        login(page, is_first=True)

        print('waiting home page to load...')
        page.wait_for_url("https://www.acmicpc.net/")
        print('success!\n')

        print('navigating to submit page...')
        page.goto(f'https://www.acmicpc.net/submit/{problem_number}')
        print('success!\n')

        print('submitting answer...')
        page.evaluate('code => document.querySelector(".CodeMirror").CodeMirror.setValue(code)', answer_code)
        page.click('[id=submit_button]')
        print('success!\n')

        print('waiting for result...')
        result_node = page.locator(
            '#status-table tbody tr:first-child .result-text:not(.result-wait, .result-compile, .result-judging)')
        result_text = result_node.text_content()
        result_class = str(result_node.evaluate("node => node.className"))
        print('success!\n')

        is_ac = 'ac' in result_class
        slack_message += 'AC를 받았습니다!' if is_ac else 'AC를 받지 못했습니다.'

        os.remove('answers/' + answer_file)
        answer_left = len(answer_files) - 1

        slack_message += f' \n채점 결과: {result_text} \n남은 문제는 {answer_left}개입니다.'

        if answer_left:
            hook_slack(slack_message, important=not is_ac)
        else:
            hook_slack(slack_message + '\n\n남은 문제가 없습니다!', important=True)

    except NoAnswerError as e:
        hook_slack(message=e.message, important=True)
    except Exception:
        hook_slack(traceback.format_exc(), important=True)
    finally:
        context.close()
        browser.close()


with sync_playwright() as playwright:
    browser = playwright.firefox.launch(headless=True)
    context = browser.new_context(locale='en-US')
    context.set_default_timeout(300000)
    run(context)
```

---

### Github Actions 워크플로 (main.yml)

1. 매일 정해진 시간에 프로그램이 실행되게 할 필요가 있다. 이는 Github Actions의 [`schedule`](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule) 이벤트를 사용하여 구현했다.
    

```yaml
name: BOJ Streak Bot

on:
  schedule:
    - cron: "50 11 * * *" # UST 11:50 -> KST 20:50
  workflow_dispatch:
```

cron 문법으로 `"50 11 * * *"` 는 매일 11시 50분에 작업을 실행한다는 의미이다. Github Actions는 UTC 기준으로 동작하므로 한국 시간(UTC+9) 기준 오후 8시 50분에 실행되는 셈이다. (cron 문법에 대해 더 알아보고 싶다면 [https://crontab.guru/](https://crontab.guru/)를 참고할 수 있다.)

왜 9시 정각으로 설정하지 않는지 의아할 수 있으나, Github Actions는 무료로 제공되며 전 세계에서 사용하므로 사람들이 몰리는 시간에는 요청이 크게 지연된다. 따라서 여유 있게 10분 전에 실행하는 것이 좋다.

---

2. 실행 환경을 세팅한다. 프로젝트 파일을 불러오고, 프로그램 실행에 필요한 파이썬 및 관련 패키지들을 설치해준다.
    

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [ 3.11 ]

    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
          fetch-depth: 0

      - name: Set up python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install python package
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Ensure browsers are installed
        run: python -m playwright install --with-deps
```

`checkout` 액션을 이용해 우분투 환경에다 레포지토리의 내용을 복사하고, `setup-python` 액션을 통해 파이썬 3.11 버전을 설치했다. 그 다음 `requirements.txt`에 명시한 파이썬 패키지들을 설치하고, `playwright install` 명령어를 통해 Playwright 사용에 필요한 추가 파일들을 설치했다.

---

3. 프로그램을 실행한다.
    

```yaml
      - name: Run program
        run: |
          python -u ./program.py ${{secrets.USER_ID}} ${{secrets.USER_PW}} ${{secrets.SLACK_BOT_TOKEN}} ${{secrets.SLACK_CHANNEL}} ${{secrets.CAPSOLVER_KEY}}
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1711611612781/0814ecee-1d8d-484b-9bb0-d33c26412b2e.png align="center")

민감한 값들(백준 아이디, 패스워드, 슬랙 토큰 등)은 레포지토리 내의 `Secrets`에 보관하고 있다가 프로그램 실행 시 전달하도록 하였다.

---

4. 변경사항을 레포지토리에 저장한다.
    

```yaml
      - name: Commit files
        run: |
          git config --local user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git commit -a -m "Remove uploaded answer"

      - name: Push changes
        uses: ad-m/github-push-action@master
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          branch: ${{ github.ref }}
```

프로그램이 정상적으로 실행되고 나면 제출 완료한 문제는 폴더에서 삭제된다. 이를 원본 레포지토리에 반영하기 위해 커밋과 푸시(`github-push-action` 액션 사용)를 진행한다.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1711612405725/9f50373b-a36c-45a8-9b84-a9427fd9b466.png align="left")

재밌는 팁이 있는데, 커밋 시 유저 이메일을 `41898282+github-actions[bot]@users.noreply.github.com` 로 설정하면 위와 같이 공식 봇이 커밋한 것처럼 표시된다.

---

전체 코드는 다음과 같다.

```yaml
name: BOJ Streak Bot

on:
  schedule:
    - cron: "50 11 * * *" # UST 11:50 -> KST 20:50
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [ 3.11 ]

    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
          fetch-depth: 0

      - name: Set up python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install python package
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Ensure browsers are installed
        run: python -m playwright install --with-deps

      - name: Run program
        run: |
          python -u ./program.py ${{secrets.USER_ID}} ${{secrets.USER_PW}} ${{secrets.SLACK_BOT_TOKEN}} ${{secrets.SLACK_CHANNEL}} ${{secrets.CAPSOLVER_KEY}}

      - name: Commit files
        run: |
          git config --local user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git commit -a -m "Remove uploaded answer"

      - name: Push changes
        uses: ad-m/github-push-action@master
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          branch: ${{ github.ref }}
```

## 🤔 후기

완성까지 이틀 정도 걸렸다. 기능 구현 자체는 첫날에 완료했는데, 캡차 관련 이슈로 삽질을 하느라 시간이 좀 많이 소요됐다. 이제 며칠 간 돌려보면서 테스트할 예정이다. 오랜 기간 동안 생각대로 잘 작동할지 기대가 된다.

현재 레포지토리는 private으로 해 두었는데, 혹시나 필요한 사람이 있다면 public으로 전환할 생각이 있다. 근데 이 정도로 스트릭에 집착하는 사람은 잘 없지 않을까...

다음은 개발에 참고한 프로젝트들이다.

* [https://github.com/xhdtlsid2/boj-streak-keeper](https://github.com/xhdtlsid2/boj-streak-keeper)
    
* [https://github.com/blurfx/BOJ-AutoSubmit](https://github.com/blurfx/BOJ-AutoSubmit)
    
* [https://github.com/Nuung/auto-lotto-gitaction](https://github.com/Nuung/auto-lotto-gitaction)