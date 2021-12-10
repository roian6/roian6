## Jetpack Compose 살짝만 맛보기 🚀

Jetpack Compose를 이용해 간단한 To-do 앱을 만들며 느낀 점과 장단점에 대해 다룹니다.

## 👀 너 누군데
고3 입시를 준비하느라 안드로이드 개발을 1년 정도 쉬었다. 그동안 있었던 굵직한 변화들을 살펴보니, 최근 혜성같이 등장한 ```Jetpack Compose```가 엄청 유행이라고 한다. 대체 컴포즈가 뭐고, 얼마나 대단하길래 ```xml```을 대체한다는 얘기까지 나오는걸까? 


![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1638094808882/OCwMqE4pl.png)

원래 안드로이드 개발에서는 앱의 레이아웃(UI)을 표현하기 위해 ```xml```을 사용해왔다. xml로 레이아웃을 먼저 작성한 뒤, 자바/코틀린 코드에서 레이아웃의 구성 요소(View)들을 호출해서 소통하는 방식이다. 하지만 이러한 방식에는 몇몇 근본적인 문제점이 존재했다.

- **Java/Kotlin 코드와 높은 의존성을 가짐**  
이미 완성된 앱에서 버튼을 하나 빼고 싶다고 하자. 단순히 xml을 수정해서 버튼을 지우면 될 것 같지만, 해당 버튼과 연결된 Java/Kotlin 코드를 함께 삭제하지 않으면 오류가 발생한다.
 
- **화면 요소의 재사용성이 낮음**  
5개의 입력 칸이 있는 회원가입 화면을 만들고자 한다. 입력 칸이 모두 똑같이 생겼더라도, 5개의 EditText를 하나하나 만들어 주어야 한다. 

- **코드가 길고 보일러플레이트가 많음**  
xml 언어 자체의 특성과 상술한 재사용성 문제로 인해, 레이아웃이 복잡할수록 코드가 비대해지고 알아보기 어려워진다.

또 기존의 View 시스템은 시간이 흐를수록 상속과 레거시 덩어리가 되어버려서, 유지보수하는 입장에서도 고민이 이만저만이 아니었을 것이다. (아티클 작성일 기준 View.java의 코드 길이는 **30409줄**이다.)

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1638091368107/0aEHSMJ1t.png)

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1638093737080/Zh-2fK5Mo.png)

>  Jetpack Compose는 네이티브 UI를 빌드하기 위한 Android의 최신 도구 키트입니다.

따라서 이를 개선하기 위해 ```Kotlin```과 ```선언형 UI```를 기반으로 만들어진 것이 [Jetpack Compose](https://developer.android.com/jetpack/compose?hl=ko)다. 컴포즈의 구성 요소들은 모두 Kotlin 함수로 만들어져 있다. 따라서 재사용이 쉽고 코드가 간결하다는 장점이 있다. 레이아웃을 작성하려고 여러 언어를 배울 필요도 없고, 구글 왈 직관적이기까지 하다. 엄청 좋아보인다. *근데 이거 어디서 본 것 같은데...*

![30fviu.jpg](https://cdn.hashnode.com/res/hashnode/image/upload/v1638097393576/aclG0AxTZ.jpeg)

[플러터](https://flutter.dev/)랑 문법적, 구조적으로 비슷한 부분이 많다. 같은 구글에서 만들기도 하고, 둘 다 기본적으로 머티리얼 디자인을 기반으로 하고 있어서 그런 것 같다. 근데 나중에 플러터가 충분히 stable 해지면 컴포즈는 'iOS 안되는 반쪽짜리 플러터'가 되는 게 아닐까? *(이미지: [Reddit](https://www.reddit.com/r/mAndroidDev/comments/bm4kmh/composing_ui_declaratively/))* 

## 🤔 일단 써보자

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1638098724163/AHPAKTeuH.png)
일단 한번 써보기로 했다. 우선  [Compose 기초 코드랩](https://developer.android.com/codelabs/jetpack-compose-basics#0)을 찾아서 수강했다. 해당 코드랩에서는 컴포즈의 기초적인 동작 원리와 UI 작성 방법, State와 LazyColumn(RecyclerView 대체)에 대해 다루고 있다. 위 이미지처럼 펼쳐지는 리스트를 만드는 것이 최종 목표다.

일단 안드로이드 진영 최대 빌런인 RecyclerView를 안 써도 되는게 너무 좋았다. 리스트 하나 띄우는데 ```ViewGroup, LayoutManager, ViewHolder, Adapter, DiffUtil, Item layout```... 이게 다 필요하다는게 말이 되나? 컴포즈에서는 ```LazyColumn```에 데이터만 넣으면 알아서 그려준다.

컴포즈의 선언형 UI도 처음에는 난해한데 쓰다 보면 조금씩 적응되는 느낌이다. 화면 구성 요소들을 함수로 잘게 쪼갤 수 있기 때문에 중첩된 레이아웃을 관리하기도 약간 더 편했다. 

## 🏃 투두리스트 만들기
이제 뭔가 만들어볼 시간이다. 마침 대외활동에서 투두리스트 앱을 만들 일이 생겨서, 기왕 만드는 김에 컴포즈로 만들어보기로 했다. 기능은 최대한 단순하게 정했다.

- Todo 생성하기
- Todo 내용 작성하기
- Todo 완료 체크하기
- Todo 삭제하기

Firebase나 Room을 붙여서 저장이 가능하도록 만들려다가 일단 보류했다. 컴포즈에서 ViewModel, LiveData을 사용해서 State를 관리하는 법을 다루는 [코드랩](https://developer.android.com/codelabs/jetpack-compose-state?hl=ko#0)이 있던데, 이거 공부한 다음에 추가해 보면 좋을 것 같다. 

완성된 앱 화면은 다음과 같다.

![Screen_Recording_20211128-174326_TODO_1.gif](https://cdn.hashnode.com/res/hashnode/image/upload/v1638090386900/YLC910BRv.gif)

### 메인 화면

```
@Composable
fun Main() {
    var list: List<Todo> by rememberSaveable { mutableStateOf(listOf()) }

    fun addTodo(todo: Todo) {
        list = list + listOf(todo)
    }

    fun editTodo(i: Int, todo: Todo) {
        list = list.toMutableList().also { it[i] = todo }
    }

    fun deleteTodo(i: Int) {
        list = list.toMutableList().also { it.removeAt(i) }
    }

    val (showDialog, setShowDialog) =
        rememberSaveable { mutableStateOf(false) }
    var deleteItem by rememberSaveable { mutableStateOf(0) }

    Scaffold(
        topBar = {
            TopBar(onAction = { addTodo(Todo()) })
        },
    ) {
        TodoList(
            list,
            onChange = { i, todo -> editTodo(i, todo) },
            onDelete = {
                deleteItem = it
                setShowDialog(true)
            }
        )
        DeleteDialog(showDialog, setShowDialog) {
            deleteTodo(deleteItem)
        }
    }
}
``` 
데이터를 이곳에서 저장하고 수정한다. 왜 리스트를 저렇게 수정하고 삭제하나 싶을텐데, 데이터가 변화했음을 트리거하기 위해서 저렇게 하는게 권장사항이라고 한다. *왜일까?*

레이아웃은 머티리얼 기반이므로 Scaffold를 사용했다. AlertDialog도 여기서 관리하는데 구현 방식이 썩 마음에 들진 않는다. 

### 리스트

```
@Composable
fun TodoList(
    todos: List<Todo>,
    onChange: (i: Int, todo: Todo) -> Unit,
    onDelete: (i: Int) -> Unit
) {
    LazyColumn(...) {
        itemsIndexed(items = todos) { i, todo ->
            TodoItem(
                item = todo,
                onChange = { onChange(i, it) },
                onDelete = { onDelete(i) }
            )
        }
    }
}
``` 
리스트를 그리는 함수다. RecyclerView와 코드 양을 비교해보면...


### 아이템

```
@Composable
fun TodoItem(item: Todo, onChange: (todo: Todo) -> Unit, onDelete: () -> Unit) {
    Card(modifier = Modifier
        ...
        .pointerInput(Unit) {
            detectTapGestures(onLongPress = { onDelete() })
        }
    ) {
        Row(...) {
            if (item.onEdit) {
                TextField(
                    value = item.text,
                    onValueChange = { onChange(item.copy(text = it)) },
                    ...
                )
                IconButton(
                    ...
                    onClick = { onChange(item.copy(onEdit = false)) }) {
                    Icon(...)
                }
            } else {
                Text(
                    text = item.text,
                    ...
                )
                Checkbox(
                    ...
                    checked = item.done,
                    onCheckedChange = { onChange(item.copy(done = it)) })
            }
        }
    }
}
``` 
작성 중일때는 TextField가, 작성을 완료했을 때는 Text가 표시되도록 조건문으로 분기했다. 길게 클릭하면 삭제할 수 있도록 리스너를 설정했다.

아이템의 내용이 변하면 이곳에서 실제 데이터를 수정하는 게 아니라 바뀐 아이템을 위로 올려보낸다(TodoItem -> TodoList -> Main). 최종적으로 Main()에서 실제 데이터를 수정하면, 바뀐 데이터를 기반으로 화면이 다시 그려지게 된다.

전체 코드는 Github에서 확인할 수 있다.

%[https://github.com/roian6/ComposeTODO]

## 🚀 그래서 쓸만한가요?
내가 잠깐 써보고 느낀 Jetpack Compose의 장단점은 다음과 같다.

### 장점
- 코드가 간결하고 나름 직관적이다.
- 레이아웃 파일을 따로 관리 안해도 된다.
- 리사이클러뷰가 없다.
- 레이아웃을 쪼개서 관리/재사용하기 좋다.

### 단점
- 자동완성이 불편하다.
- 미리보기가 정말 불편하다.
- 아직 지원 안 하는 기능이 많다.  
(ex. LazyColumn은 애니메이션 지원이 안 된다.)
- 만들다 만 것 같은 느낌이다.

종합하면 장점은 확실한데, 정식 출시 치고는 아직 stable 하지 않은 느낌이다. 트위터 앱이 컴포즈를 사용했다고 하던데 이걸 어떻게 프로덕트에 적용했는지 궁금해진다. 그 이면에는 안드로이드 팀의 피땀눈물이 있지 않았을까?

그래도 구글이 컴포즈를 많이 밀어주고 있으니 일단 공부해두면 좋을 것 같다. 

---

안드로이드 개발을 잠깐 쉬었던 만큼, 많이 공부해서 감도 살리고 모던한 기술도 써보고 싶다.