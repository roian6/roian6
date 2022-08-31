## 내 웹 사이트, 앱 스토어에 출시하는 법 🛫

안드로이드 WebView를 이용해 웹 사이트를 앱처럼 만드는 팁을 다룹니다.

## 🤔 들어가며

> 저희 서비스가 웹으로 개발되어 있는데, 이걸 앱으로 만들어서 Google Play에 출시하고 싶어요. 

안드로이드 개발을 공부하면서 주변으로부터 종종 이런 요청을 들은 적이 있다.  
이런 경우에 사용할 수 있는 방법 중 하나로 Android [WebView](https://developer.android.com/guide/webapps/webview?hl=ko)가 있다.

웹뷰는 안드로이드 앱에서 웹 페이지를 표시하기 위해 제공되는 View 컴포넌트로, 이를 잘 활용하면 앱 개발 분야 경험이 없더라도 어렵지 않게 웹 사이트를 안드로이드 앱으로 옮겨 올 수 있다.

이 방식에는 다음과 같은 장단이 있다.

### 장점

- **구현 비용 절감**  
앞선 사례처럼 서비스가 이미 웹으로 구현되어 있는 경우, 네이티브 앱을 새로 개발하는 것보다 웹뷰로 이를 포팅하는 것이 개발 시간, 관리 비용의 측면에서 더 유리할 수 있다.

- **쉬운 업데이트 반영**  
Google Play에 업로드한 앱을 수정하려면 새로운 버전을 만들어 심사를 요청해야 하는데, 이 심사에 꽤 오랜 시간이 소요되며 거절당하는 경우도 종종 발생한다. 반면 웹뷰로 구현된 앱은 웹 페이지를 배포하기만 하면 변경 사항이 앱에 실시간으로 반영된다는 큰 이점을 가진다.

- **디바이스 기능 접근**  
단순 웹 브라우저를 통해 서비스를 제공하는 것과 비교했을 때, 카메라나 모션 센서 등 휴대폰에 내장된 기능을 사용할 수 있으며 이를 이용해 QR 인식, 흔들어서 실행 등의 기능을 구현할 수 있다. (푸시 알림 또한 보낼 수 있다.)

### 단점

- **상대적으로 낮은 퍼포먼스**  
네이티브 방식으로 구현된 앱과 비교했을 때, 하드웨어 자원을 100% 활용하기 어렵기 때문에 반응 속도의 차이가 다소 발생할 수 있다. 이러한 단점은 아래와 같은 상황에서 더욱 부각된다.

- **인터넷 연결에 의존**  
웹 사이트를 로딩해서 보여주는 방식이므로, 인터넷 연결이 불안정하다면 화면을 불러오는 데 많은 시간이 소요되거나 실패할 수도 있다. 

따라서 처음부터 웹뷰 사용을 상정하고 서비스 전체를 웹으로 개발하기보다, 이미 서비스가 웹으로 구현되어 있는 경우 활용하거나 잦은 업데이트가 필요한 화면만 웹뷰로 구현하는 전략을 권장하고 싶다.  
(웹 기술을 이용해 앱을 개발하고 싶다면 [React Native](https://reactnative.dev/)를 활용할 수 있다.)

## 🏃 Step by Step

[네이버](m.naver.com)를 앱으로 만드는 예제를 통해 구현 과정을 살펴보자. 

### Android Studio 설치

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661777538783/6gqydojOB.png align="left")

Android Studio는 안드로이드 앱 개발에 사용되는 IDE로, [공식 페이지](https://developer.android.com/studio)에서 최신 버전을 설치할 수 있다. 자세한 설치 과정은 [공식 문서](https://developer.android.com/studio/install?hl=ko), [관련 블로그](https://ineedtoprogramandweb.tistory.com/entry/AndroidStudio-%EC%95%88%EB%93%9C%EB%A1%9C%EC%9D%B4%EB%93%9C-%EC%8A%A4%ED%8A%9C%EB%94%94%EC%98%A4-%EC%84%A4%EC%B9%98%ED%95%98%EA%B8%B0-%EC%B5%9C%EC%8B%A0)나 검색을 통해 확인할 수 있다. 

정상적으로 설치가 완료되면 다음과 같은 화면을 볼 수 있다. (버전에 따라 조금씩 다를 수 있다.)

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661831879988/wwZLpU6hZ.png align="left")

### 프로젝트 세팅

위 화면에서 'New Project'를 누르고, 다음과 같은 과정을 진행하면 된다.

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661832123350/lnG2whGqa.png align="left")

'Empty Activity'를 선택 후, Next를 클릭한다.

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661832224675/ZCl1lURxH.png align="left")

- **Name**  
원하는 프로젝트명을 기입한다.
- **Package Name**  
앱의 패키지명을 기입한다. com.<닉네임>.<프로젝트명> 정도로 입력하면 된다.
- **Save Location**  
프로젝트 파일 경로를 설정한다. 경로에 공백이나 한글이 포함되지 않도록 한다.
- **Language**  
[Kotlin](https://developer.android.com/kotlin?hl=ko)을 선택한다.
- **Minimum SDK**  
지원할 [안드로이드 버전](https://developer.android.com/studio/releases/platforms?hl=ko)을 설정할 수 있다. 잘 모르겠다면 API 23(6.0)을 권장한다.

모두 입력하고 Finish를 누르면 아래처럼 새로운 프로젝트가 만들어진다.

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661833168183/-7wkrqrhE.png align="left")

안드로이드 개발이 처음이라면 아래 링크를 통해 프로젝트 구조를 먼저 파악해보는 것을 추천한다.

%[https://developer.android.com/training/basics/firstapp/creating-project?hl=ko]

### 웹뷰 구현하기

프로젝트에 웹뷰를 적용하는 과정은 다음과 같다.

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661833232885/uFmgBpI0-.png align="left")

화면 왼쪽의 탐색기에서 ```activity_main.xml``` 파일을 찾고 더블클릭하여 연다.

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661833399900/NvqggfaIZ.png align="left")

위처럼 작성되어 있는 코드를 다음과 같이 수정한다. 

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661833754739/Fzui1GgKG.png align="left")

```
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <WebView
        android:id="@+id/webView"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

</LinearLayout>
``` 

해당 파일은 안드로이드 앱의 레이아웃을 그리는 역할을 한다. 작성한 코드는 화면에 꽉 차도록(match_parent) 웹뷰를 표시하겠다는 의미이다. 해당 웹뷰를 호출하여 사용할 수 있도록 'webView'라는 id를 부여했다.

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661841824411/DUXgznkfB.png align="left")

마찬가지로 ```MainActivity.kt``` 파일을 찾아 열고, 아래 사진과 같이 코드를 추가해 준다.

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661859768679/X0RDtxCUu.png align="left")

```
private lateinit var webView: WebView // 웹뷰 변수 선언

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)

    webView = findViewById(R.id.webView) // 웹뷰 객체 가져오기
    webView.webViewClient = WebViewClient() // 웹뷰 클라이언트 생성
    webView.loadUrl("https://m.naver.com") // 해당 url 로딩
}

``` 
해당 파일에서 앱의 주요 기능을 구현한다. 작성한 코드는 레이아웃에 있는 웹뷰 객체를 불러오고, 해당 웹뷰 상에서 url을 로딩하겠다는 의미이다. 

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661845720138/kt4gG-_0z.png align="left")

마지막으로 ```AndroidManifest.xml``` 파일을 열고 다음 코드를 추가해준다.

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661859928347/EI4KCZNDOl.png align="left")

```
<uses-permission android:name="android.permission.INTERNET"/>
``` 
앱에서 인터넷을 사용할 것임에 대한 권한을 명시하는 코드다.

---

여기까지 작성을 완료했다면 실제 기기나 에뮬레이터에서 개발한 앱을 실행해보자. 실행 방법을 잘 모르겠다면 [공식 문서](https://developer.android.com/training/basics/firstapp/running-app?hl=ko)에서 확인할 수 있다.

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661854764036/tHaZhNE2Z.png align="left")

성공적으로 m.naver.com을 안드로이드 앱에서 실행할 수 있다!

그런데 이 상태에서는 몇 가지 문제점이 존재한다. 

1. **화면 위쪽에 의도하지 않았던 보라색 툴바가 생긴다. **
2. **사이트 로딩이 불완전하다.**
3. **뒤로가기를 누르면 이전 페이지로 가지 않고 앱이 종료된다.**
4. **화면 방향을 전환하면 웹사이트가 다시 로딩된다.**

보다 그럴싸한 앱을 만들기 위해 이 문제들을 해결해보자.

### 최적화하기

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661858213393/nokivXr-Y.png align="left")

**보라색 툴바** 문제는 앱에 기본으로 적용되어 있는 테마 때문에 발생한다. res/values/에서 ```themes.xml``` 파일을 찾아 열고, 사진의 ```DarkActionBar``` 부분을  ```NoActionBar```로 수정해준다.

![스크린샷 2022-08-30 오후 7.52.19.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661857324273/mWLTY5kSa.png align="left")

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661857045947/f2Tkf7KGl.png align="left")

```themes.xml``` 파일이 일반 버전과 night(다크모드) 버전으로 총 2개가 존재하는데, 두 파일 모두 수정해주면 된다. 여기에 추가로 statusBar(휴대폰 최상단의 배터리 잔량이 표시되는 영역)의 색상을 변경하고 싶다면 다음과 같이 코드를 변경할 수 있다.

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661857832999/q8RhyNxd_.png align="left")

```
<item name="android:statusBarColor" tools:targetApi="l">@color/white</item>
<item name="android:windowLightStatusBar">true</item> 
// 다크모드에선 @color/black, false로 설정
``` 
각각 statusBar 색상을 흰색으로, statusBar 아이콘 색상을 검은색으로 변경하는 코드이다. 모두 적용하고 실행하면 다음과 같은 결과를 얻을 수 있다.

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661858232266/Z7t8vasEf.png align="left")

---

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661858544483/O-HGZhVsi.png align="left")

**불완전한 로딩**은 웹뷰 상에서 기본적으로 JavaScript가 비활성화되어 있어 발생한다. ```MainActivity.kt```에 아래 코드를 추가해준다.

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661861734604/ONx9wXRRv.png align="left")

```
webView.settings.javaScriptEnabled = true
```
이 옵션을 활성화하면 웹뷰에서 자바스크립트를 실행할 수 있다. (단 [보안](https://support.google.com/faqs/answer/7668153?hl=en)에 유의할 필요가 있다.) 적용하고 나면 사이트가 정상적으로 로딩된다. 

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661861348245/In-ISyvcN.png align="left")

---

**뒤로가기 시 앱이 종료**되는 문제를 해결하기 위해, ```MainActivity.kt```에 아래 코드를 추가해준다.

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661862381184/FyofLT4QH.png align="left")

```
override fun onBackPressed() {
    if (webView.canGoBack()) webView.goBack()
    else super.onBackPressed()
}
``` 

휴대폰의 뒤로가기 버튼을 눌렀을 때의 동작을 수정하는 코드이다. 뒤로 갈 페이지가 있다면 웹뷰 상에서 뒤로가기를 수행하고, 없다면 앱을 종료하도록 하여 기대한 결과를 얻을 수 있다. 

---

**화면 방향 전환** 시 안드로이드에서는 화면을 지우고 새로 그리는데, 이때 ```onCreate``` 함수가 다시 실행되어 웹뷰의 url 또한 다시 로딩되는 문제가 생긴다. 자세한 내용은 [공식 문서](https://developer.android.com/guide/topics/resources/runtime-changes?hl=ko)에서 확인할 수 있다.

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661877384144/m0E4BYMZY.png align="left")

```
if (savedInstanceState != null) webView.restoreState(savedInstanceState)
else webView.loadUrl("https://m.naver.com")
``` 

```
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    webView.saveState(outState)
}
``` 
이를 방지하기 위해 화면 상태를 저장하는 state를 활용할 수 있다. 먼저 state를 웹뷰에 저장해두고, ```onCreate```가 다시 실행되었을 때는 url을 다시 로딩하는 것이 아니라 저장된 state를 불러와 보여주는 방식이다.

---

%[https://youtube.com/shorts/gKuGV56PaWI?feature=share]

웹 사이트를 꽤 그럴싸하게 앱으로 옮겨 올 수 있게 되었다.

추가로 알아두면 좋은 내용들은 다음과 같다.

- **http 연결 허용**  
https 미지원 등으로 웹뷰에서 http를 꼭 사용해야 하는 경우, Manifest 파일에 ```android:usesCleartextTraffic="true"```를 추가해야 앱이 정상적으로 작동한다. (보안상 권장되진 않는다.)

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661884157642/lMO9ZBKoR.png align="left")

- **localStorage 이용**  
웹에서 localStorage를 이용하는 경우, 앱을 재실행 했을때도 데이터가 남아있게 하려면 웹뷰의 setting에 ```domStorageEnabled = true```를 추가하면 된다. 

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661884453740/ks61T0x9R.png align="left")

## 💌 웹 사이트와 통신하기

앞서 웹 사이트를 앱에 포팅하는 과정을 간단하게 살펴보았다. 그런데 내 웹 사이트에서 휴대폰의 기능을 이용하고 싶은 경우(ex. 웹 페이지의 버튼을 누르면 QR코드 인식), 또는 반대로 휴대폰에서 웹 사이트의 함수를 호출하고 싶은 경우(ex. 휴대폰을 흔들면 특정 페이지로 이동)에는 어떻게 할까?

이럴 때는 웹뷰의 [Bridge](https://developer.android.com/guide/webapps/webview?hl=ko#EnablingJavaScript)라는 기능을 활용할 수 있다. 예제를 통해 알아보자.


```
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="initial-scale=1.0">
    <meta charset="utf-8">
</head>
<body>

<div>Bridge 통신 예제입니다.</div>

<input type="button" value="안드로이드 함수 호출" onClick="androidToast('Hello from javascript!')"/>

<div id='div'></div>

<script type="text/javascript">

    function androidToast(text) {
        Android.showToast(text);
    }

    function showText(text) {
        document.getElementById('div').textContent = text
    }

</script>
</body>
</html>
``` 
버튼을 누르면 안드로이드 상의 함수를 실행하는 간단한 웹 코드이다. 텍스트를 화면에 보여주는 함수도 하나 만들었다. (https://roian6.github.io/WebViewExample/에서 확인할 수 있다.)

안드로이드의 함수를 실행하는 부분을 보면 ```Android.showToast()```와 같은 방식으로 접근하고 있는 것을 알 수 있다. 이 ```Android```는 앱에서 웹뷰로 주입된 인터페이스로, 사용하려면 ```MainActivity.kt```에 다음과 같이 코드를 작성할 수 있다.

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661912808012/x6UgYEoDd.png align="left")

```
inner class WebAppInterface {
    @JavascriptInterface
    fun showToast(text: String) {
        Toast.makeText(this@MainActivity, text, Toast.LENGTH_SHORT).show()
    }
}
``` 

```
webView.addJavascriptInterface(WebAppInterface(), "Android")
``` 
클래스를 하나 만들어 내부에 함수를 구현하는데, 이때 ```@JavascriptInterface``` 어노테이션을 달아주면 해당 함수를 웹에서 호출할 수 있게 된다. 

만든 클래스를 ```webView.addJavascriptInterface()```를 통해 원하는 인터페이스명과 함께 웹뷰로 넘겨주면 된다.

![ezgif.com-gif-maker.gif](https://cdn.hashnode.com/res/hashnode/image/upload/v1661913819777/eAUkfZAE4.gif align="left")

이제 웹 페이지에서 앱 내부의 함수를 실행할 수 있게 되었다!

---

반대로 앱에서 웹 페이지의 함수를 실행하는 예제는 다음과 같다. 


![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661913975481/AqOOBVr70.png align="left")


```
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <WebView
        android:id="@+id/webView"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_margin="24dp"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
``` 

![image.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1661914147616/hzFZxb9OL.png align="left")

```
val button = findViewById<FloatingActionButton>(R.id.button)
    button.setOnClickListener {
        webView.evaluateJavascript("showText('Hello from Android!')") {
            // String으로 return 값을 받을 수 있음
        }
    }
``` 

앱의 우측 하단에 버튼을 하나 추가했고, 해당 버튼을 눌렀을 때 ```webView.evaluateJavascript()```를 통해 웹 페이지의 함수를 호출하도록 했다. 실행해보면 다음과 같은 결과를 얻을 수 있다.

![ezgif.com-gif-maker (1).gif](https://cdn.hashnode.com/res/hashnode/image/upload/v1661914438174/tl2VOnwQN.gif align="left")

이렇게 Bridge를 통해 앱과 웹 사이에서 자유로운 통신이 가능하다. 

## 🛫 출시할 때 고려할 것

앞서 웹뷰를 이용해 웹 사이트를 앱 위에 올리고, 실제 앱처럼 사용할 수 있도록 최적화하는 방법에 대해 알아보았다. 마지막으로 만든 앱을 Google Paly에 출시하기 전 고려하면 좋은 사항에 대해 정리해 보았다.

- **앱 아이콘 적용하기**  
%[https://developer.android.com/codelabs/basic-android-kotlin-training-change-app-icon]

- **스플래시 화면 적용하기**  
%[https://developer.android.com/develop/ui/views/launch/splash-screen]

- **도메인 소유권 증명 (중요)**  
웹뷰를 이용한 앱을 스토어에 출시할 경우, 해당 웹 사이트의 소유권이 자신에게 있다는 것을 함께 알려주어야 한다. [관련 블로그](https://satisfactoryplace.tistory.com/256)에서 자세한 내용을 참고할 수 있다.

---

## 👏 마치며

예제 소스 코드는 아래 깃허브에서 확인할 수 있습니다.

%[https://github.com/roian6/WebViewExample]

안드로이드 개발 경험이 없더라도 따라해 볼 수 있도록 코드는 최대한 간결하게 유지했고, 구현이 복잡한 내용(intent scheme 대응 등)은 우선 제외했습니다. 

> 소프트웨어 마에스트로 컨퍼런스(8/31) 발표를 위해 작성한 게시물입니다!