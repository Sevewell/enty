/**
 * 日付時点指定UI のJavaScript
 */

// URL パラメータから日付を取得する関数  
function getDateFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('view_date');
}

// URL パラメータに日付を設定する関数
function setDateInUrl(date) {
    const url = new URL(window.location);
    if (date) {
        url.searchParams.set('view_date', date);
    } else {
        url.searchParams.delete('view_date');
    }
    
    // ページをリロードして新しい日付でデータを取得
    // 他のパラメータ（type等）は保持される
    window.location.href = url.toString();
}

// 現在の日付をYYYY-MM-DD形式で取得
function getCurrentDate() {
    const today = new Date();
    return today.toISOString().split('T')[0];
}

// DOM読み込み完了時の処理
document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.getElementById('viewDate');
    const applyButton = document.getElementById('applyDate');
    const resetButton = document.getElementById('resetDate');
    
    if (!dateInput || !applyButton || !resetButton) {
        return; // 要素が見つからない場合は何もしない
    }
    
    // URLから日付を取得してinputに設定
    const urlDate = getDateFromUrl();
    if (urlDate) {
        dateInput.value = urlDate;
    } else {
        // URLに日付がない場合は現在日を設定
        dateInput.value = getCurrentDate();
    }
    
    // 適用ボタンのクリック処理
    applyButton.addEventListener('click', function() {
        const selectedDate = dateInput.value;
        if (selectedDate) {
            setDateInUrl(selectedDate);
        }
    });
    
    // 現在ボタンのクリック処理
    resetButton.addEventListener('click', function() {
        const currentDate = getCurrentDate();
        dateInput.value = currentDate;
        setDateInUrl(currentDate);
    });
    
    // Enterキーでも適用
    dateInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            applyButton.click();
        }
    });
});
