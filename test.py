const LINE_ACCESS_TOKEN = 'd8CcLX9ZybtYOHeAorTYHJQ6CT6vQG5S2c7oSIdRLsd1FG5Pto09P5HymdqX6w43DCOyK90Qh84onvNVqGnK+LY/JrW5GZOv3W57BBHwjrNKuoJglaa/OZOv3oUOKo4MXdrw8+6h3NrPSoC/S3Ft7wdB04t89/1O/w1cDnyilFU='

function doPost(e) {
  const event = JSON.parse(e.postData.contents).events[0]
  const replyToken = event.replyToken;
  const userId = event.source.userId; // USER_IDを取得
  
  let userMessage = event.message.text;
  
  // スプレッドシートを取得
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  
  // 「終了」メッセージの場合は処理終了
  if (userMessage === "終了") {
    return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
  }
  
  // 「○○月」の形式かチェック
  const monthPattern = /^(\d{1,2})月$/;
  const monthMatch = userMessage.match(monthPattern);
  
  // 「○○日」の形式かチェック
  const dayPattern = /^(\d{1,2})日$/;
  const dayMatch = userMessage.match(dayPattern);
  
  // 「○件目」の形式かチェック
  const itemPattern = /^(\d+)件目$/;
  const itemMatch = userMessage.match(itemPattern);
  
  // 半角数字かチェック（売上金額）
  const isHalfWidthNumber = /^[0-9]+$/.test(userMessage);
  
  // 「今日」メッセージの処理
  const isTodayMessage = (userMessage === "今日");
  
  // 「今日_入金」メッセージの処理
  const isTodayDepositMessage = (userMessage === "今日_入金");
  
  // 「入金」メッセージの処理（新規追加）
  const isDepositMessage = (userMessage === "入金");
  
  // 「抽出」メッセージの処理
  const isExtractMessage = (userMessage === "抽出");
  
  // 「詳細が知りたい」メッセージの処理
  const isDetailMessage = (userMessage === "詳細が知りたい");
  
  // 期間抽出メッセージの処理
  const isTodayExtractMessage = (userMessage === "今日_抽出");
  const isYesterdayExtractMessage = (userMessage === "昨日_抽出");
  const isThisMonthExtractMessage = (userMessage === "今月_抽出");
  const isLastMonthExtractMessage = (userMessage === "先月_抽出");
  
  // 「○月_入金」の形式かチェック
  const monthDepositPattern = /^(\d{1,2})月_入金$/;
  const monthDepositMatch = userMessage.match(monthDepositPattern);
  
  // 「○日_入金」の形式かチェック
  const dayDepositPattern = /^(\d{1,2})日_入金$/;
  const dayDepositMatch = userMessage.match(dayDepositPattern);
  
  // 「teamA」「teamB」メッセージの処理
  const isTeamAMessage = (userMessage === "teamA");
  const isTeamBMessage = (userMessage === "teamB");
  const isTeamCMessage = (userMessage === "teamC");
  
  // チーム判定とtempシートの取得
  let currentTeam = "A"; // デフォルトはA
  let tempSheet = null;

  // 各チームのtempシートを確認して現在のチームを判定
  const teams = ["A", "B", "C"];
  let foundActiveTeam = false;

  for (const team of teams) {
    const checkSheet = spreadsheet.getSheetByName("temp" + team);
    if (checkSheet) {
      try {
        const teamStatus = checkSheet.getRange("F1").getValue();
        const statusStr = String(teamStatus).trim();
        
        if (statusStr === "team" + team) {
          currentTeam = team;
          tempSheet = checkSheet;
          foundActiveTeam = true;
          break;
        }
      } catch (error) {
        // エラーが発生した場合は次のチームをチェック
        continue;
      }
    }
  }

  // アクティブなチームが見つからない場合はデフォルトを使用
  if (!foundActiveTeam || !tempSheet) {
    const defaultSheetName = "temp" + currentTeam;
    tempSheet = spreadsheet.getSheetByName(defaultSheetName);
    
    if (!tempSheet) {
      // デフォルトのtempシートが存在しない場合は作成
      tempSheet = spreadsheet.insertSheet(defaultSheetName);
    }
  }

  let waitingForAmount = false;
  let waitingForTime = false;
  let waitingForDeposit = false;
  let waitingForGas = false;
  let waitingForDetailPeriod = false;
  
  if (tempSheet) {
    const waitingFlag = tempSheet.getRange("D1").getValue();
    waitingForAmount = (waitingFlag === "waiting_for_amount");
    waitingForTime = (waitingFlag === "waiting_for_time");
    waitingForDeposit = (waitingFlag === "waiting_for_deposit");
    waitingForGas = (waitingFlag === "waiting_for_gas");
    waitingForDetailPeriod = (waitingFlag === "waiting_for_detail_period");
  }
  
  // 「記録」メッセージの処理
  const isRecordMessage = (userMessage === "記録");
  
  // 「売上」メッセージの処理
  const isSalesCashMessage = (userMessage === "売上(現金)");
  const isSalesCreditMessage = (userMessage === "売上(クレジット)");
  const isSalesInvoiceMessage = (userMessage === "売上(請求書)");
  
  // 「リセット」メッセージの処理
  const isResetMessage = (userMessage === "リセット");
  
  if (isResetMessage) {
    // 「リセット」メッセージの場合 - 全チームのtempシートをクリア
    const allTempSheets = ["tempA", "tempB", "tempC"];
    for (const sheetName of allTempSheets) {
      const sheet = spreadsheet.getSheetByName(sheetName);
      if (sheet) {
        sheet.clear();
      }
    }
    
    const url = 'https://api.line.me/v2/bot/message/reply';
    UrlFetchApp.fetch(url, {
      'headers': {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
      },
      'method': 'post',
      'payload': JSON.stringify({
        'replyToken': replyToken,
        'messages': [
          {
            'type': 'text',
            'text': '状態をリセットしました。',
          },
          {
            'type': 'text',
            'text': '実行タイプを選んでください。',
          }
        ]
      })
    });
    
    return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    
  } else if (isSalesCashMessage) {
      // 売上タイプを保存
      tempSheet.getRange("G1").setValue("現金");

      // 「売上」メッセージの場合
      const url = 'https://api.line.me/v2/bot/message/reply';
      UrlFetchApp.fetch(url, {
        'headers': {
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
        },
        'method': 'post',
        'payload': JSON.stringify({
          'replyToken': replyToken,
          'messages': [
            {
              'type': 'text',
              'text': '売上金額（円）を入力してください。',
            }
          ]
        })
      });
      
      return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
      
      
  } else if (isSalesCreditMessage) {
      // 売上タイプを保存
      tempSheet.getRange("G1").setValue("クレジット");
      
      // 「売上」メッセージの場合
      const url = 'https://api.line.me/v2/bot/message/reply';
      UrlFetchApp.fetch(url, {
        'headers': {
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
        },
        'method': 'post',
        'payload': JSON.stringify({
          'replyToken': replyToken,
          'messages': [
            {
              'type': 'text',
              'text': '売上金額（円）を入力してください。',
            }
          ]
        })
      });
      
      return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
      
  } else if (isSalesInvoiceMessage) {
      // 売上タイプを保存
      tempSheet.getRange("G1").setValue("請求書");

      // 「売上」メッセージの場合
      const url = 'https://api.line.me/v2/bot/message/reply';
      UrlFetchApp.fetch(url, {
        'headers': {
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
        },
        'method': 'post',
        'payload': JSON.stringify({
          'replyToken': replyToken,
          'messages': [
            {
              'type': 'text',
              'text': '売上金額（円）を入力してください。',
            }
          ]
        })
      });
      
      return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
  } else if (userMessage === "売上") {
    // 「売上」メッセージの場合
    const url = 'https://api.line.me/v2/bot/message/reply';
    UrlFetchApp.fetch(url, {
      'headers': {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
      },
      'method': 'post',
      'payload': JSON.stringify({
        'replyToken': replyToken,
        'messages': [
          {
            'type': 'text',
            'text': '売上記録を開始します。',
          },
          {
            'type': 'text',
            'text': '何件目ですか？',
          }
        ]
      })
    });
    
    return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);    
  } else if (isRecordMessage) {
    // 「記録」メッセージの場合
    const url = 'https://api.line.me/v2/bot/message/reply';
    UrlFetchApp.fetch(url, {
      'headers': {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
      },
      'method': 'post',
      'payload': JSON.stringify({
        'replyToken': replyToken,
        'messages': [
          {
            'type': 'text',
            'text': '記録モードです。',
          },
          {
            'type': 'text',
            'text': 'チームを選択してください。',
          }
        ]
      })
    });
    
    return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    
  } else if (isTeamAMessage) {
    // 「teamA」メッセージの場合
    tempSheet = spreadsheet.getSheetByName("tempA");
    
    // F1セルにteamA状態を保存
    tempSheet.getRange("F1").setValue("teamA");
    // currentTeam変数も更新
    currentTeam = "A";
    
    // 完了メッセージを送信
    const url = 'https://api.line.me/v2/bot/message/reply';
    UrlFetchApp.fetch(url, {
      'headers': {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
      },
      'method': 'post',
      'payload': JSON.stringify({
        'replyToken': replyToken,
        'messages': [
          {
            'type': 'text',
            'text': 'チームAに切り替えました。',
          },
          {
            'type': 'text',
            'text': 'いつを記録しますか？',
          }
        ]
      })
    });
    
    return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    
  } else if (isTeamBMessage) {
    // 「teamB」メッセージの場合
    tempSheet = spreadsheet.getSheetByName("tempB");
    
    // F1セルにteamB状態を保存
    tempSheet.getRange("F1").setValue("teamB");
    // currentTeam変数も更新
    currentTeam = "B";
    
    // 完了メッセージを送信
    const url = 'https://api.line.me/v2/bot/message/reply';
    UrlFetchApp.fetch(url, {
      'headers': {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
      },
      'method': 'post',
      'payload': JSON.stringify({
        'replyToken': replyToken,
        'messages': [
          {
            'type': 'text',
            'text': 'チームBに切り替えました。',
          },
          {
            'type': 'text',
            'text': 'いつを記録しますか？',
          }
        ]
      })
    });
    
    return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
  } else if (isTeamCMessage) {
    // 「teamC」メッセージの場合
    tempSheet = spreadsheet.getSheetByName("tempC");
    
    // F1セルにteamC状態を保存
    tempSheet.getRange("F1").setValue("teamC");
    // currentTeam変数も更新
    currentTeam = "C";
    
    // 完了メッセージを送信
    const url = 'https://api.line.me/v2/bot/message/reply';
    UrlFetchApp.fetch(url, {
      'headers': {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
      },
      'method': 'post',
      'payload': JSON.stringify({
        'replyToken': replyToken,
        'messages': [
          {
            'type': 'text',
            'text': 'チームCに切り替えました。',
          },
          {
            'type': 'text',
            'text': 'いつを記録しますか？',
          }
        ]
      })
    });
    
    return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
  } else if (isExtractMessage) {
    // 「抽出」メッセージの場合
    const url = 'https://api.line.me/v2/bot/message/reply';
    UrlFetchApp.fetch(url, {
      'headers': {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
      },
      'method': 'post',
      'payload': JSON.stringify({
        'replyToken': replyToken,
        'messages': [
          {
          'type': 'text',
          'text': '抽出モードです。',
          },
          {
          'type': 'text',
          'text': '上記から、期間を選択してください。',
          }
        ]
      })
    });
    
    return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    
  } else if (isDetailMessage) {
    // 「詳細が知りたい」メッセージの場合
    // 現在のチームのtempシートを取得
    tempSheet = spreadsheet.getSheetByName("temp" + currentTeam);
    if (tempSheet) {
      // 既存のtempシートをクリア
      tempSheet.clear();
    }
    
    // 詳細表示の期間入力待ちフラグを設定
    tempSheet.getRange("D1").setValue("waiting_for_detail_period");
    
    const url = 'https://api.line.me/v2/bot/message/reply';
    UrlFetchApp.fetch(url, {
      'headers': {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
      },
      'method': 'post',
      'payload': JSON.stringify({
        'replyToken': replyToken,
        'messages': [
          {
          'type': 'text',
          'text': '詳細を見たい期間を選択してください：「今月」「先月」',
          }
        ]
      })
    });
    
    return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    
  } else if (waitingForDetailPeriod) {
    // 詳細表示の期間入力を処理
    const now = new Date();
    let targetMonth = null;
    let periodName = "";
    
    if (userMessage === "今月") {
      targetMonth = (now.getMonth() + 1) + "月";
      periodName = "今月";
    } else if (userMessage === "先月") {
      const lastMonth = new Date(now);
      lastMonth.setMonth(now.getMonth() - 1);
      targetMonth = (lastMonth.getMonth() + 1) + "月";
      periodName = "先月";
    } else {
      // 不正な期間の場合
      const url = 'https://api.line.me/v2/bot/message/reply';
      UrlFetchApp.fetch(url, {
        'headers': {
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
        },
        'method': 'post',
        'payload': JSON.stringify({
          'replyToken': replyToken,
          'messages': [{
            'type': 'text',
            'text': '「今月」「先月」のいずれかを選択してください。',
          }]
        })
      });
      
      return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    }
    
    if (targetMonth && tempSheet) {
      // シートを取得
      const monthSheetName = currentTeam + "_売上・時間当たり売上高管理表_" + targetMonth;
      let monthSheet = spreadsheet.getSheetByName(monthSheetName);
      
      if (monthSheet) {
        try {
          // シートのデータを取得
          const data = monthSheet.getDataRange().getValues();
          let extractedData = [];
          
          // 月全体の詳細データを抽出
          for (let i = 0; i < data.length; i++) {
            const day = data[i][0]; // A列の日付
            if (day && day !== "" && day !== "日付" && typeof day === "string" && day.includes("日")) {
              let dayData = [];
              let hasSalesData = false;
              
              // 各件目のデータを抽出
              for (let itemNum = 1; itemNum <= 4; itemNum++) {
                const salesColIndex = (itemNum - 1) * 2 + 1; // 1件目:B(1), 2件目:D(3), 3件目:F(5), 4件目:H(7)
                const timeColIndex = salesColIndex + 1; // 時間列は売上列の次
                
                const salesValue = data[i][salesColIndex];
                const timeValue = data[i][timeColIndex];
                
                if (salesValue !== "" && salesValue !== null && salesValue !== undefined && salesValue !== 0) {
                  const timeText = timeValue && timeValue !== 0 ? timeValue + "分" : "時間未記録";
                  dayData.push(itemNum + "件目:" + salesValue + "円(" + timeText + ")");
                  hasSalesData = true;
                }
              }
              
              if (hasSalesData && dayData.length > 0) {
                extractedData.push(day + " " + dayData.join(" "));
              }
            }
          }
          
          // フラグをクリア
          tempSheet.getRange("D1").setValue("");
          
          // 結果をメッセージとして返信
          let resultMessage = "";
          if (extractedData.length > 0) {
            resultMessage = periodName + "(" + targetMonth + ")のデータ:\n" + extractedData.join("\n");
          } else {
            resultMessage = periodName + "のデータがありません。";
          }
          
          const url = 'https://api.line.me/v2/bot/message/reply';
          UrlFetchApp.fetch(url, {
            'headers': {
              'Content-Type': 'application/json; charset=UTF-8',
              'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
            },
            'method': 'post',
            'payload': JSON.stringify({
              'replyToken': replyToken,
              'messages': [
                {
                  'type': 'text',
                  'text': resultMessage,
                }
              ]
            })
          });
          
          return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
          
        } catch (error) {
          // エラーが発生した場合
          const url = 'https://api.line.me/v2/bot/message/reply';
          UrlFetchApp.fetch(url, {
            'headers': {
              'Content-Type': 'application/json; charset=UTF-8',
              'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
            },
            'method': 'post',
            'payload': JSON.stringify({
              'replyToken': replyToken,
              'messages': [
                {
                  'type': 'text',
                  'text': 'データの抽出中にエラーが発生しました。',
                }
              ]
            })
          });
          
          return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
        }
      } else {
        // シートが存在しない場合
        const url = 'https://api.line.me/v2/bot/message/reply';
        UrlFetchApp.fetch(url, {
          'headers': {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
        },
        'method': 'post',
        'payload': JSON.stringify({
          'replyToken': replyToken,
          'messages': [
            {
              'type': 'text',
              'text': monthSheetName + 'が見つかりません。',
            }
          ]
        })
      });
      
      return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    }
  }
    
  } else if (isTodayExtractMessage || isYesterdayExtractMessage || isThisMonthExtractMessage || isLastMonthExtractMessage) {
    // 期間抽出メッセージの処理（両チーム対応版）
    const now = new Date();
    let targetDate = null;
    let targetMonth = null;
    let isMonthMode = false;
    let periodName = "";
    
    if (isTodayExtractMessage) {
      targetDate = now.getDate() + "日";
      targetMonth = (now.getMonth() + 1) + "月";
      periodName = "今日";
    } else if (isYesterdayExtractMessage) {
      const yesterday = new Date(now);
      yesterday.setDate(now.getDate() - 1);
      targetDate = yesterday.getDate() + "日";
      targetMonth = (yesterday.getMonth() + 1) + "月";
      periodName = "昨日";
    } else if (isThisMonthExtractMessage) {
      targetMonth = (now.getMonth() + 1) + "月";
      isMonthMode = true;
      periodName = "今月";
    } else if (isLastMonthExtractMessage) {
      const lastMonth = new Date(now);
      lastMonth.setMonth(now.getMonth() - 1);
      targetMonth = (lastMonth.getMonth() + 1) + "月";
      isMonthMode = true;
      periodName = "先月";
    }
    
    if (targetMonth) {
      // 両チームのシート名を構築
      const teamASheetName = "A_現金管理表_" + targetMonth;
      const teamBSheetName = "B_現金管理表_" + targetMonth;
      const teamCSheetName = "C_現金管理表_" + targetMonth;
      
      let teamASheet = spreadsheet.getSheetByName(teamASheetName);
      let teamBSheet = spreadsheet.getSheetByName(teamBSheetName);
      let teamCSheet = spreadsheet.getSheetByName(teamCSheetName);
      
      let teamAData = { sales: 0, time: 0, found: false, days: 0, workingDays: 0 };
      let teamBData = { sales: 0, time: 0, found: false, days: 0, workingDays: 0 };
      let teamCData = { sales: 0, time: 0, found: false, days: 0, workingDays: 0 };
      let resultMessages = [];
      
      try {
        // teamAのデータを取得
        if (teamASheet) {
          const dataA = teamASheet.getDataRange().getValues();
          
          if (isMonthMode) {
            // 月モード：全日付行を巡回して売上タイプ別に集計
            let cashSales = 0, creditSales = 0, invoiceSales = 0;
            for (let i = 0; i < dataA.length; i++) {
              const day = dataA[i][0]; // A列の日付
              if (day && day !== "" && day !== "日付" && typeof day === "string" && day.includes("日")) {
                const rowData = dataA[i];
                
                // 1〜4件目をチェック
                for (let itemNum = 1; itemNum <= 4; itemNum++) {
                  const amountCol = (itemNum - 1) * 2 + 1; // B,D,F,H
                  const typeCol = (itemNum - 1) * 2 + 2;   // C,E,G,I
                  
                  const amount = rowData[amountCol];
                  const type = rowData[typeCol];
                  
                  if (amount && amount !== 0 && type) {
                    if (type === "現金") cashSales += parseInt(amount);
                    else if (type === "クレジット") creditSales += parseInt(amount);
                    else if (type === "請求書") invoiceSales += parseInt(amount);
                  }
                }
              }
            }

            if (cashSales > 0 || creditSales > 0 || invoiceSales > 0) {
              teamAData.sales = cashSales + creditSales + invoiceSales;
              teamAData.cashSales = cashSales;
              teamAData.creditSales = creditSales;
              teamAData.invoiceSales = invoiceSales;
              teamAData.found = true;
            }
            
            // 稼働日数をカウント（別のループ）
            for (let i = 0; i < dataA.length; i++) {
              const day = dataA[i][0]; // A列の日付
              if (day && day !== "" && day !== "日付" && typeof day === "string" && day.includes("日")) {
                const rowData = dataA[i];
                let hasSalesData = false;
                
                // 各件目のデータをチェック
                for (let itemNum = 1; itemNum <= 4; itemNum++) {
                  const salesColIndex = (itemNum - 1) * 2 + 1;
                  const salesValue = rowData[salesColIndex];
                  
                  if (salesValue !== "" && salesValue !== null && salesValue !== undefined && salesValue !== 0) {
                    hasSalesData = true;
                    break;
                  }
                }
                
                if (hasSalesData) {
                  teamAData.workingDays++;
                }
              }
            }
            
          } else {
            // 日モード：特定の日のデータを売上タイプ別に集計
            for (let i = 0; i < dataA.length; i++) {
              if (dataA[i][0] === targetDate) {
                const rowData = dataA[i];
                let cashSales = 0, creditSales = 0, invoiceSales = 0;
                let hasSalesData = false;
                
                // 各件目のデータを売上タイプ別に抽出
                for (let itemNum = 1; itemNum <= 4; itemNum++) {
                  const amountCol = (itemNum - 1) * 2 + 1; // B,D,F,H
                  const typeCol = (itemNum - 1) * 2 + 2;   // C,E,G,I
                  
                  const amount = rowData[amountCol];
                  const type = rowData[typeCol];
                  
                  if (amount && amount !== 0 && type) {
                    if (type === "現金") cashSales += parseInt(amount);
                    else if (type === "クレジット") creditSales += parseInt(amount);
                    else if (type === "請求書") invoiceSales += parseInt(amount);
                    hasSalesData = true;
                  }
                }
                
                if (hasSalesData) {
                  teamAData.sales = cashSales + creditSales + invoiceSales;
                  teamAData.cashSales = cashSales;
                  teamAData.creditSales = creditSales;
                  teamAData.invoiceSales = invoiceSales;
                  teamAData.found = true;
                  teamAData.days = 1;
                }
                break;
              }
            }
          }
        }
        
        // teamBのデータを取得（teamAと同じロジック）
        if (teamBSheet) {
          const dataB = teamBSheet.getDataRange().getValues();
          
          if (isMonthMode) {
            // 月モード：全日付行を巡回して売上タイプ別に集計
            let cashSales = 0, creditSales = 0, invoiceSales = 0;
            for (let i = 0; i < dataB.length; i++) {
              const day = dataB[i][0]; // A列の日付
              if (day && day !== "" && day !== "日付" && typeof day === "string" && day.includes("日")) {
                const rowData = dataB[i];
                
                // 1〜4件目をチェック
                for (let itemNum = 1; itemNum <= 4; itemNum++) {
                  const amountCol = (itemNum - 1) * 2 + 1; // B,D,F,H
                  const typeCol = (itemNum - 1) * 2 + 2;   // C,E,G,I
                  
                  const amount = rowData[amountCol];
                  const type = rowData[typeCol];
                  
                  if (amount && amount !== 0 && type) {
                    if (type === "現金") cashSales += parseInt(amount);
                    else if (type === "クレジット") creditSales += parseInt(amount);
                    else if (type === "請求書") invoiceSales += parseInt(amount);
                  }
                }
              }
            }

            if (cashSales > 0 || creditSales > 0 || invoiceSales > 0) {
              teamBData.sales = cashSales + creditSales + invoiceSales;
              teamBData.cashSales = cashSales;
              teamBData.creditSales = creditSales;
              teamBData.invoiceSales = invoiceSales;
              teamBData.found = true;
            }
            
            // 稼働日数をカウント（別のループ）
            for (let i = 0; i < dataB.length; i++) {
              const day = dataB[i][0]; // A列の日付
              if (day && day !== "" && day !== "日付" && typeof day === "string" && day.includes("日")) {
                const rowData = dataB[i];
                let hasSalesData = false;
                
                // 各件目のデータをチェック
                for (let itemNum = 1; itemNum <= 4; itemNum++) {
                  const salesColIndex = (itemNum - 1) * 2 + 1;
                  const salesValue = rowData[salesColIndex];
                  
                  if (salesValue !== "" && salesValue !== null && salesValue !== undefined && salesValue !== 0) {
                    hasSalesData = true;
                    break;
                  }
                }
                
                if (hasSalesData) {
                  teamBData.workingDays++;
                }
              }
            }
          } else {
            // 日モード：特定の日のデータを売上タイプ別に集計
            for (let i = 0; i < dataB.length; i++) {
              if (dataB[i][0] === targetDate) {
                const rowData = dataB[i];
                let cashSales = 0, creditSales = 0, invoiceSales = 0;
                let hasSalesData = false;
                
                // 各件目のデータを売上タイプ別に抽出
                for (let itemNum = 1; itemNum <= 4; itemNum++) {
                  const amountCol = (itemNum - 1) * 2 + 1; // B,D,F,H
                  const typeCol = (itemNum - 1) * 2 + 2;   // C,E,G,I
                  
                  const amount = rowData[amountCol];
                  const type = rowData[typeCol];
                  
                  if (amount && amount !== 0 && type) {
                    if (type === "現金") cashSales += parseInt(amount);
                    else if (type === "クレジット") creditSales += parseInt(amount);
                    else if (type === "請求書") invoiceSales += parseInt(amount);
                    hasSalesData = true;
                  }
                }
                
                if (hasSalesData) {
                  teamBData.sales = cashSales + creditSales + invoiceSales;
                  teamBData.cashSales = cashSales;
                  teamBData.creditSales = creditSales;
                  teamBData.invoiceSales = invoiceSales;
                  teamBData.found = true;
                  teamBData.days = 1;
                }
                break;
              }
            }
          }
        }
        
        // teamCのデータを取得（teamAと同じロジック）
        if (teamCSheet) {
          const dataC = teamCSheet.getDataRange().getValues();
          
          if (isMonthMode) {
            // 月モード：全日付行を巡回して売上タイプ別に集計
            let cashSales = 0, creditSales = 0, invoiceSales = 0;
            for (let i = 0; i < dataC.length; i++) {
              const day = dataC[i][0]; // A列の日付
              if (day && day !== "" && day !== "日付" && typeof day === "string" && day.includes("日")) {
                const rowData = dataC[i];
                
                // 1〜4件目をチェック
                for (let itemNum = 1; itemNum <= 4; itemNum++) {
                  const amountCol = (itemNum - 1) * 2 + 1; // B,D,F,H
                  const typeCol = (itemNum - 1) * 2 + 2;   // C,E,G,I
                  
                  const amount = rowData[amountCol];
                  const type = rowData[typeCol];
                  
                  if (amount && amount !== 0 && type) {
                    if (type === "現金") cashSales += parseInt(amount);
                    else if (type === "クレジット") creditSales += parseInt(amount);
                    else if (type === "請求書") invoiceSales += parseInt(amount);
                  }
                }
              }
            }

            if (cashSales > 0 || creditSales > 0 || invoiceSales > 0) {
              teamCData.sales = cashSales + creditSales + invoiceSales;
              teamCData.cashSales = cashSales;
              teamCData.creditSales = creditSales;
              teamCData.invoiceSales = invoiceSales;
              teamCData.found = true;
            }
            
            // 稼働日数をカウント（別のループ）
            for (let i = 0; i < dataC.length; i++) {
              const day = dataC[i][0]; // A列の日付
              if (day && day !== "" && day !== "日付" && typeof day === "string" && day.includes("日")) {
                const rowData = dataC[i];
                let hasSalesData = false;
                
                // 各件目のデータをチェック
                for (let itemNum = 1; itemNum <= 4; itemNum++) {
                  const salesColIndex = (itemNum - 1) * 2 + 1;
                  const salesValue = rowData[salesColIndex];
                  
                  if (salesValue !== "" && salesValue !== null && salesValue !== undefined && salesValue !== 0) {
                    hasSalesData = true;
                    break;
                  }
                }
                
                if (hasSalesData) {
                  teamCData.workingDays++;
                }
              }
            }
          } else {
            // 日モード：特定の日のデータを売上タイプ別に集計
            for (let i = 0; i < dataC.length; i++) {
              if (dataC[i][0] === targetDate) {
                const rowData = dataC[i];
                let cashSales = 0, creditSales = 0, invoiceSales = 0;
                let hasSalesData = false;
                
                // 各件目のデータを売上タイプ別に抽出
                for (let itemNum = 1; itemNum <= 4; itemNum++) {
                  const amountCol = (itemNum - 1) * 2 + 1; // B,D,F,H
                  const typeCol = (itemNum - 1) * 2 + 2;   // C,E,G,I
                  
                  const amount = rowData[amountCol];
                  const type = rowData[typeCol];
                  
                  if (amount && amount !== 0 && type) {
                    if (type === "現金") cashSales += parseInt(amount);
                    else if (type === "クレジット") creditSales += parseInt(amount);
                    else if (type === "請求書") invoiceSales += parseInt(amount);
                    hasSalesData = true;
                  }
                }
                
                if (hasSalesData) {
                  teamCData.sales = cashSales + creditSales + invoiceSales;
                  teamCData.cashSales = cashSales;
                  teamCData.creditSales = creditSales;
                  teamCData.invoiceSales = invoiceSales;
                  teamCData.found = true;
                  teamCData.days = 1;
                }
                break;
              }
            }
          }
        }

        // 結果の作成
        if (isMonthMode) {
          resultMessages.push(periodName + "(" + targetMonth + ") 両チーム合計");
        } else {
          resultMessages.push(periodName + "(" + targetMonth + targetDate + ") 両チーム合計");
        }
        
        // teamA結果
        if (teamAData.found) {
          const hoursA = Math.floor(teamAData.time / 60);
          const minutesA = teamAData.time % 60;
          const salesPerMinuteA = teamAData.time > 0 ? Math.round(teamAData.sales / teamAData.time * 60) : 0;
          let timeDisplayA = "";
          if (hoursA > 0 && minutesA > 0) {
            timeDisplayA = hoursA + "時間" + minutesA + "分";
          } else if (hoursA > 0) {
            timeDisplayA = hoursA + "時間";
          } else {
            timeDisplayA = minutesA + "分";
          }
          
          resultMessages.push("【チームA】");
          resultMessages.push("現金売上: " + (teamAData.cashSales || 0).toLocaleString() + "円");
          resultMessages.push("クレジット売上: " + (teamAData.creditSales || 0).toLocaleString() + "円");
          resultMessages.push("請求書売上: " + (teamAData.invoiceSales || 0).toLocaleString() + "円");
          resultMessages.push("合計売上: " + teamAData.sales.toLocaleString() + "円");

          if (isMonthMode && teamAData.workingDays > 0) {
            const dailyAverageSalesA = Math.round(teamAData.sales / teamAData.workingDays);
            resultMessages.push("日単位売上: " + dailyAverageSalesA.toLocaleString() + "円 (÷" + teamAData.workingDays + "稼働日)");
          }
        } else {
          resultMessages.push("【チームA】データなし");
        }
        
        // teamB結果
        if (teamBData.found) {
          const hoursB = Math.floor(teamBData.time / 60);
          const minutesB = teamBData.time % 60;
          const salesPerMinuteB = teamBData.time > 0 ? Math.round(teamBData.sales / teamBData.time * 60) : 0;
          let timeDisplayB = "";
          if (hoursB > 0 && minutesB > 0) {
            timeDisplayB = hoursB + "時間" + minutesB + "分";
          } else if (hoursB > 0) {
            timeDisplayB = hoursB + "時間";
          } else {
            timeDisplayB = minutesB + "分";
          }
          
          resultMessages.push("【チームB】");
          resultMessages.push("現金売上: " + (teamBData.cashSales || 0).toLocaleString() + "円");
          resultMessages.push("クレジット売上: " + (teamBData.creditSales || 0).toLocaleString() + "円");
          resultMessages.push("請求書売上: " + (teamBData.invoiceSales || 0).toLocaleString() + "円");
          resultMessages.push("合計売上: " + teamBData.sales.toLocaleString() + "円");

          if (isMonthMode && teamBData.workingDays > 0) {
            const dailyAverageSalesB = Math.round(teamBData.sales / teamBData.workingDays);
            resultMessages.push("日単位売上: " + dailyAverageSalesB.toLocaleString() + "円 (÷" + teamBData.workingDays + "稼働日)");
          }
        } else {
          resultMessages.push("【チームB】データなし");
        }
        
        // teamC結果
        if (teamCData.found) {
          const hoursC = Math.floor(teamCData.time / 60);
          const minutesC = teamCData.time % 60;
          const salesPerMinuteC = teamCData.time > 0 ? Math.round(teamCData.sales / teamCData.time * 60) : 0;
          let timeDisplayC = "";
          if (hoursC > 0 && minutesC > 0) {
            timeDisplayC = hoursC + "時間" + minutesC + "分";
          } else if (hoursC > 0) {
            timeDisplayC = hoursC + "時間";
          } else {
            timeDisplayC = minutesC + "分";
          }
          
          resultMessages.push("【チームC】");
          resultMessages.push("現金売上: " + (teamCData.cashSales || 0).toLocaleString() + "円");
          resultMessages.push("クレジット売上: " + (teamCData.creditSales || 0).toLocaleString() + "円");
          resultMessages.push("請求書売上: " + (teamCData.invoiceSales || 0).toLocaleString() + "円");
          resultMessages.push("合計売上: " + teamCData.sales.toLocaleString() + "円");

          if (isMonthMode && teamCData.workingDays > 0) {
            const dailyAverageSalesC = Math.round(teamCData.sales / teamCData.workingDays);
            resultMessages.push("日単位売上: " + dailyAverageSalesC.toLocaleString() + "円 (÷" + teamCData.workingDays + "稼働日)");
          }
        } else {
          resultMessages.push("【チームC】データなし");
        }

        // 合計計算
        if (teamAData.found || teamBData.found || teamCData.found) {
          const totalSales = teamAData.sales + teamBData.sales + teamCData.sales;
          const totalTime = teamAData.time + teamBData.time + teamCData.time;
          const totalDays = teamAData.days + teamBData.days + teamCData.days;
          
          const totalHours = Math.floor(totalTime / 60);
          const totalMinutes = totalTime % 60;
          const totalSalesPerMinute = totalTime > 0 ? Math.round(totalSales / totalTime * 60) : 0;
          let totalTimeDisplay = "";
          if (totalHours > 0 && totalMinutes > 0) {
            totalTimeDisplay = totalHours + "時間" + totalMinutes + "分";
          } else if (totalHours > 0) {
            totalTimeDisplay = totalHours + "時間";
          } else {
            totalTimeDisplay = totalMinutes + "分";
          }
          
          resultMessages.push("【全チーム合計】");
          resultMessages.push("合計売上: " + totalSales.toLocaleString() + "円");
          resultMessages.push("合計稼働時間: " + totalTimeDisplay + " (" + totalTime + "分)");
          resultMessages.push("時間単位売上: " + totalSalesPerMinute.toLocaleString() + "円/時間");

          const totalWorkingDays = teamAData.workingDays + teamBData.workingDays + teamCData.workingDays;
          if (totalWorkingDays > 0) {
            const totalDailyAverageSales = Math.round(totalSales / totalWorkingDays);
            resultMessages.push("日単位売上: " + totalDailyAverageSales.toLocaleString() + "円/日");
          }
        } else {
          resultMessages.push("【両チーム合計】データなし");
        }
        
        // 結果をメッセージとして返信
        const url = 'https://api.line.me/v2/bot/message/reply';
        UrlFetchApp.fetch(url, {
          'headers': {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
          },
          'method': 'post',
          'payload': JSON.stringify({
            'replyToken': replyToken,
            'messages': [
              {
                'type': 'text',
                'text': resultMessages.join("\n"),
              }
            ]
          })
        });
        
        return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
        
      } catch (error) {
        // エラーが発生した場合
        const url = 'https://api.line.me/v2/bot/message/reply';
        UrlFetchApp.fetch(url, {
          'headers': {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
          },
          'method': 'post',
          'payload': JSON.stringify({
            'replyToken': replyToken,
            'messages': [
              {
                'type': 'text',
                'text': 'データの抽出中にエラーが発生しました。',
              }
            ]
          })
        });
        
        return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
      }
    }
  } else if (monthMatch) {
    // 月のメッセージの場合
    // tempシートのA1に月を記録
    tempSheet.getRange("A1").setValue(userMessage);
    
    // 対応する月シートも作成（存在しない場合）
    const monthSheetName = currentTeam + "_現金管理表_" + userMessage;
    let monthSheet = spreadsheet.getSheetByName(monthSheetName);
    if (!monthSheet) {
      monthSheet = spreadsheet.insertSheet(monthSheetName);
    }
    
    // 完了メッセージを送信
    const url = 'https://api.line.me/v2/bot/message/reply';
    UrlFetchApp.fetch(url, {
      'headers': {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
      },
      'method': 'post',
      'payload': JSON.stringify({
        'replyToken': replyToken,
        'messages': [
          {
            'type': 'text',
            'text': userMessage + 'を設定しました。',
          }
        ]
      })
    });
    
    return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    
  } else if (isTodayMessage) {
    // 「今日」メッセージの場合
    const now = new Date();
    const currentMonth = now.getMonth() + 1; // 月は0ベースなので+1
    const currentDay = now.getDate();
    const monthText = currentMonth + "月";
    const dayText = currentDay + "日";
    
    // tempシートに月と日を記録
    tempSheet.getRange("A1").setValue(monthText);
    tempSheet.getRange("B1").setValue(dayText);
    
    // 対応する月シートも作成（存在しない場合）
    const monthSheetName = currentTeam + "_現金管理表_" + monthText;
    let monthSheet = spreadsheet.getSheetByName(monthSheetName);
    if (!monthSheet) {
      monthSheet = spreadsheet.insertSheet(monthSheetName);
    }
    
    // 売上・時間当たり売上高管理表も作成（存在しない場合）
    const timeSheetName = currentTeam + "_売上・時間当たり売上高管理表_" + monthText;
    let timeSheet = spreadsheet.getSheetByName(timeSheetName);
    if (!timeSheet) {
      timeSheet = spreadsheet.insertSheet(timeSheetName);
    }
    
    // 完了メッセージを送信
    const url = 'https://api.line.me/v2/bot/message/reply';
    UrlFetchApp.fetch(url, {
      'headers': {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
      },
      'method': 'post',
      'payload': JSON.stringify({
        'replyToken': replyToken,
        'messages': [
          {
            'type': 'text',
            'text': '今日(' + monthText + dayText + ')を設定しました。',
          },
          {
            'type': 'text',
            'text': '売上ですか？入金・ガソリン他ですか？',
          }
        ]
      })
    });
    
    return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    
  } else if (isTodayDepositMessage) {
    // 「今日_入金」メッセージの場合
    const now = new Date();
    const currentMonth = now.getMonth() + 1; // 月は0ベースなので+1
    const currentDay = now.getDate();
    const monthText = currentMonth + "月";
    const dayText = currentDay + "日";
    
    // tempシートに月と日を記録
    tempSheet.getRange("A1").setValue(monthText);
    tempSheet.getRange("B1").setValue(dayText);
    
    // 入金金額待ちフラグを設定
    tempSheet.getRange("D1").setValue("waiting_for_deposit");
    
    // 対応する月シートも作成（存在しない場合）
    const monthSheetName = currentTeam + "_現金管理表_" + monthText;
    let monthSheet = spreadsheet.getSheetByName(monthSheetName);
    if (!monthSheet) {
      monthSheet = spreadsheet.insertSheet(monthSheetName);
    }
    
    // 入金金額入力を求めるメッセージを返信
    const url = 'https://api.line.me/v2/bot/message/reply';
    UrlFetchApp.fetch(url, {
      'headers': {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
      },
      'method': 'post',
      'payload': JSON.stringify({
        'replyToken': replyToken,
        'messages': [{
          'type': 'text',
          'text': '入金金額（円）を入力してください。',
        }]
      })
    });
    
    return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    
  } else if (isDepositMessage) {
    // 「入金」メッセージの処理（新規追加）
    if (tempSheet) {
      const month = tempSheet.getRange("A1").getValue();
      const day = tempSheet.getRange("B1").getValue();
      
      if (month && day) {
        // 入金金額待ちフラグを設定
        tempSheet.getRange("D1").setValue("waiting_for_deposit");
        
        // 対応する月シートも作成（存在しない場合）
        const monthSheetName = currentTeam + "_現金管理表_" + month;
        let monthSheet = spreadsheet.getSheetByName(monthSheetName);
        if (!monthSheet) {
          monthSheet = spreadsheet.insertSheet(monthSheetName);
        }
        
        // 入金金額入力を求めるメッセージを返信
        const url = 'https://api.line.me/v2/bot/message/reply';
        UrlFetchApp.fetch(url, {
          'headers': {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
          },
          'method': 'post',
          'payload': JSON.stringify({
            'replyToken': replyToken,
            'messages': [{
              'type': 'text',
              'text': '入金金額（円）を入力してください。',
            }]
          })
        });
        
        return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
      } else {
        // 月日が設定されていない場合のエラーメッセージ
        const url = 'https://api.line.me/v2/bot/message/reply';
        UrlFetchApp.fetch(url, {
          'headers': {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
          },
          'method': 'post',
          'payload': JSON.stringify({
            'replyToken': replyToken,
            'messages': [
              {
                'type': 'text',
                'text': '先に日付を設定してください。',
              }
            ]
          })
        });
        
        return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
      }
    } else {
      // tempシートが存在しない場合のエラーメッセージ
      const url = 'https://api.line.me/v2/bot/message/reply';
      UrlFetchApp.fetch(url, {
        'headers': {
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
        },
        'method': 'post',
        'payload': JSON.stringify({
          'replyToken': replyToken,
          'messages': [
            {
              'type': 'text',
              'text': '先に日付を設定してください。',
            }
          ]
        })
      });
      
      return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    }
    
  } else if (monthDepositMatch) {
    // 「○月_入金」メッセージの場合
    const monthText = monthDepositMatch[1] + "月";
    
    // tempシートのA1に月を記録
    tempSheet.getRange("A1").setValue(monthText);
    
    // 対応する月シートも作成（存在しない場合）
    const monthSheetName = currentTeam + "_現金管理表_" + monthText;
    let monthSheet = spreadsheet.getSheetByName(monthSheetName);
    if (!monthSheet) {
      monthSheet = spreadsheet.insertSheet(monthSheetName);
    }
    
    // 完了メッセージを送信
    const url = 'https://api.line.me/v2/bot/message/reply';
    UrlFetchApp.fetch(url, {
      'headers': {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
      },
      'method': 'post',
      'payload': JSON.stringify({
        'replyToken': replyToken,
        'messages': [
          {
            'type': 'text',
            'text': monthText + '_入金を設定しました。',
          }
        ]
      })
    });
    
    return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    
  } else if (dayDepositMatch) {
    // 「○日_入金」メッセージの場合
    const dayText = dayDepositMatch[1] + "日";
    
    if (tempSheet) {
      // tempシートから月を取得
      const month = tempSheet.getRange("A1").getValue();
      
      if (month) {
        // tempシートのB1に日を記録
        tempSheet.getRange("B1").setValue(dayText);
        
        // 入金金額待ちフラグを設定
        tempSheet.getRange("D1").setValue("waiting_for_deposit");
        
        // 対応する月シートも作成（存在しない場合）
        const monthSheetName = currentTeam + "_現金管理表_" + month;
        let monthSheet = spreadsheet.getSheetByName(monthSheetName);
        if (!monthSheet) {
          monthSheet = spreadsheet.insertSheet(monthSheetName);
        }
        
        // 入金金額入力を求めるメッセージを返信
        const url = 'https://api.line.me/v2/bot/message/reply';
        UrlFetchApp.fetch(url, {
          'headers': {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
          },
          'method': 'post',
          'payload': JSON.stringify({
            'replyToken': replyToken,
            'messages': [{
              'type': 'text',
              'text': '入金金額（円）を入力してください。',
            }]
          })
        });
        
        return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
      } else {
        // 月が設定されていない場合のエラーメッセージ
        const url = 'https://api.line.me/v2/bot/message/reply';
        UrlFetchApp.fetch(url, {
          'headers': {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
          },
          'method': 'post',
          'payload': JSON.stringify({
            'replyToken': replyToken,
            'messages': [
              {
                'type': 'text',
                'text': '先に「○月_入金」形式で月を設定してください。',
              }
            ]
          })
        });
        
        return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
      }
    } else {
      // tempシートが存在しない場合のエラーメッセージ
      const url = 'https://api.line.me/v2/bot/message/reply';
      UrlFetchApp.fetch(url, {
        'headers': {
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
        },
        'method': 'post',
        'payload': JSON.stringify({
          'replyToken': replyToken,
          'messages': [
            {
              'type': 'text',
              'text': '先に「○月_入金」形式で月を設定してください。',
            }
          ]
        })
      });
      
      return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    }
    
  } else if (dayMatch) {
    // 日のメッセージの場合
    if (tempSheet) {
      // tempシートのB1に日を記録
      tempSheet.getRange("B1").setValue(userMessage);
      
      // 完了メッセージを送信
      const url = 'https://api.line.me/v2/bot/message/reply';
      UrlFetchApp.fetch(url, {
        'headers': {
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
        },
        'method': 'post',
        'payload': JSON.stringify({
          'replyToken': replyToken,
          'messages': [
            {
              'type': 'text',
              'text': userMessage + 'を設定しました。',
            },
            {
              'type': 'text',
              'text': '売上ですか？入金・ガソリン他ですか？',
            }
          ]
        })
      });
      
      return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    }
    
  } else if (itemMatch) {
    // 件目のメッセージの場合
    const itemNumber = parseInt(itemMatch[1]);
    // 1件目→B列、2件目→C列、3件目→D列、4件目→E列...
    const columnLetter = String.fromCharCode(65 + itemNumber * 2 - 1); // 1件目→B(66), 2件目→D(68), 3件目→F(70), 4件目→H(72)
    
    if (tempSheet) {
      // tempシートのC1に列文字を記録
      tempSheet.getRange("C1").setValue(columnLetter);
      // 売上金額待ちフラグを設定
      tempSheet.getRange("D1").setValue("waiting_for_amount");
      
      // デバッグ用：どの列に設定されたかをログ出力
      console.log("件数: " + itemNumber + ", 列: " + columnLetter);
    }
    
    // 売上金額入力を求めるメッセージを返信
    const url = 'https://api.line.me/v2/bot/message/reply';
    UrlFetchApp.fetch(url, {
      'headers': {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
      },
      'method': 'post',
      'payload': JSON.stringify({
        'replyToken': replyToken,
        'messages': [{
          'type': 'text',
          'text': '現金ですか？クレジットですか？請求書ですか？',
        }]
      })
    });
    
    return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    
  } else if (waitingForDeposit) {
    // 「今日_入金」の後の入金金額入力を処理
    if (!isHalfWidthNumber) {
      // 半角数字でない場合はエラーメッセージを返信
      const url = 'https://api.line.me/v2/bot/message/reply';
      UrlFetchApp.fetch(url, {
        'headers': {
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
        },
        'method': 'post',
        'payload': JSON.stringify({
          'replyToken': replyToken,
          'messages': [{
            'type': 'text',
            'text': '1: 半角数字で再度回答してください',
          }]
        })
      });
      return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // 半角数字の場合は入金金額として処理
    if (tempSheet) {
      // tempシートから情報を取得
      const month = tempSheet.getRange("A1").getValue();
      const day = tempSheet.getRange("B1").getValue();
      
      if (month && day) {
        // 月シートを取得
        const monthSheetName = currentTeam + "_現金管理表_" + month;
        let monthSheet = spreadsheet.getSheetByName(monthSheetName);
        if (monthSheet) {
          // 月シートで日付の行を探す
          const data = monthSheet.getDataRange().getValues();
          let dayRow = -1;
          
          // A列で日付を検索
          for (let i = 0; i < data.length; i++) {
            if (data[i][0] === day) {
              dayRow = i + 1; // 1ベースの行番号
              break;
            }
          }
          
          // 日付の行が見つからない場合は新規追加
          if (dayRow === -1) {
            const lastRow = monthSheet.getLastRow() + 1;
            monthSheet.getRange("A" + lastRow).setValue(day);
            dayRow = lastRow;
          }
          
          // 入金金額をM列に記録
          monthSheet.getRange("M" + dayRow).setValue(parseInt(userMessage));
          
          // ガソリン代他待ちフラグを設定
          tempSheet.getRange("D1").setValue("waiting_for_gas");
          
          // ガソリン代他の金額入力を求めるメッセージを返信
          const url = 'https://api.line.me/v2/bot/message/reply';
          UrlFetchApp.fetch(url, {
            'headers': {
              'Content-Type': 'application/json; charset=UTF-8',
              'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
            },
            'method': 'post',
            'payload': JSON.stringify({
              'replyToken': replyToken,
              'messages': [{
                'type': 'text',
                'text': 'ガソリン代他の金額（円）を入力してください。',
              }]
            })
          });
          
          return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
        }
      }
    }
    
  } else if (waitingForGas) {
    // ガソリン代他の金額入力を処理
    if (!isHalfWidthNumber) {
      // 半角数字でない場合はエラーメッセージを返信
      const url = 'https://api.line.me/v2/bot/message/reply';
      UrlFetchApp.fetch(url, {
        'headers': {
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
        },
        'method': 'post',
        'payload': JSON.stringify({
          'replyToken': replyToken,
          'messages': [{
            'type': 'text',
            'text': '2: 半角数字で再度回答してください',
          }]
        })
      });
      return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // 半角数字の場合はガソリン代他の金額として処理
    if (tempSheet) {
      // tempシートから情報を取得
      const month = tempSheet.getRange("A1").getValue();
      const day = tempSheet.getRange("B1").getValue();
      
      if (month && day) {
        // 月シートを取得
        const monthSheetName = currentTeam + "_現金管理表_" + month;
        let monthSheet = spreadsheet.getSheetByName(monthSheetName);
        if (monthSheet) {
          // 月シートで日付の行を探す
          const data = monthSheet.getDataRange().getValues();
          let dayRow = -1;
          
          // A列で日付を検索
          for (let i = 0; i < data.length; i++) {
            if (data[i][0] === day) {
              dayRow = i + 1; // 1ベースの行番号
              break;
            }
          }
          
          // 日付の行が見つからない場合は新規追加（通常は既に存在するはず）
          if (dayRow === -1) {
            const lastRow = monthSheet.getLastRow() + 1;
            monthSheet.getRange("A" + lastRow).setValue(day);
            dayRow = lastRow;
          }
          
          // ガソリン代他の金額をN列に記録
          monthSheet.getRange("N" + dayRow).setValue(parseInt(userMessage));
          
          // フラグをクリア
          tempSheet.getRange("C1:E1").clearContent();
          tempSheet.getRange("G1").clearContent();
          
          // 完了メッセージを返信
          const url = 'https://api.line.me/v2/bot/message/reply';
          UrlFetchApp.fetch(url, {
            'headers': {
              'Content-Type': 'application/json; charset=UTF-8',
              'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
            },
            'method': 'post',
            'payload': JSON.stringify({
              'replyToken': replyToken,
              'messages': [
                {
                  'type': 'text',
                  'text': '入金とガソリン代他を記録しました。',
                }
              ]
            })
          });
          
          return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
        }
      }
    }  
  } else if (waitingForAmount) {
    // 「○件目」の後の入力を処理
    if (!isHalfWidthNumber) {
      // 半角数字でない場合はエラーメッセージを返信
      const url = 'https://api.line.me/v2/bot/message/reply';
      UrlFetchApp.fetch(url, {
        'headers': {
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
        },
        'method': 'post',
        'payload': JSON.stringify({
          'replyToken': replyToken,
          'messages': [{
            'type': 'text',
            'text': '3: 半角数字で再度回答してください',
          }]
        })
      });
      return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // 半角数字の場合は売上金額として処理
    if (tempSheet) {
      // tempシートから情報を取得
      const month = tempSheet.getRange("A1").getValue();
      const day = tempSheet.getRange("B1").getValue();
      const columnLetter = tempSheet.getRange("C1").getValue();
      const salesType = tempSheet.getRange("G1").getValue(); // 売上タイプを取得
      
      if (month && day && columnLetter) {
        // 売上金額をtempシートに保存
        tempSheet.getRange("E1").setValue(userMessage);
        
        // 全ての売上タイプで稼働時間待ちフラグを設定
        tempSheet.getRange("D1").setValue("waiting_for_time");
        
        // 稼働時間入力を求めるメッセージを返信
        const url = 'https://api.line.me/v2/bot/message/reply';
        UrlFetchApp.fetch(url, {
          'headers': {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
          },
          'method': 'post',
          'payload': JSON.stringify({
            'replyToken': replyToken,
            'messages': [{
              'type': 'text',
              'text': '稼働時間（分）を入力してください。',
            }]
          })
        });
        
        return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
      }
    }
    
  } else if (waitingForTime) {
    // 稼働時間の入力を処理（クレジット・請求書のみ）
    if (!isHalfWidthNumber) {
      // 半角数字でない場合はエラーメッセージを返信
      const url = 'https://api.line.me/v2/bot/message/reply';
      UrlFetchApp.fetch(url, {
        'headers': {
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
        },
        'method': 'post',
        'payload': JSON.stringify({
          'replyToken': replyToken,
          'messages': [{
            'type': 'text',
            'text': '4: 半角数字で再度回答してください',
          }]
        })
      });
      return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // 半角数字の場合は稼働時間として処理
    if (tempSheet) {
      // tempシートから情報を取得
      const month = tempSheet.getRange("A1").getValue();
      const day = tempSheet.getRange("B1").getValue();
      const columnLetter = tempSheet.getRange("C1").getValue();
      const salesAmount = tempSheet.getRange("E1").getValue();
      const salesType = tempSheet.getRange("G1").getValue(); // 売上タイプを取得
      
      if (month && day && columnLetter && (salesAmount !== null && salesAmount !== undefined && salesAmount !== "")) {
        // 全ての売上タイプで現金管理表に記録
        const monthSheetName = currentTeam + "_現金管理表_" + month;
        let monthSheet = spreadsheet.getSheetByName(monthSheetName);
        if (monthSheet) {
          // 月シートで日付の行を探す
          const data = monthSheet.getDataRange().getValues();
          let dayRow = -1;
          
          // A列で日付を検索
          for (let i = 0; i < data.length; i++) {
            if (data[i][0] === day) {
              dayRow = i + 1; // 1ベースの行番号
              break;
            }
          }
          
          // 日付の行が見つからない場合は新規追加
          if (dayRow === -1) {
            const lastRow = monthSheet.getLastRow() + 1;
            monthSheet.getRange("A" + lastRow).setValue(day);
            dayRow = lastRow;
          }
          
          // 売上金額と売上タイプを記録
          const amountColumn = columnLetter; // B, D, F, H
          const typeColumn = String.fromCharCode(columnLetter.charCodeAt(0) + 1); // C, E, G, I
          
          monthSheet.getRange(amountColumn + dayRow).setValue(parseInt(salesAmount));
          monthSheet.getRange(typeColumn + dayRow).setValue(salesType);
        }
        
        // 全ての売上タイプで売上・時間当たり売上高管理表に記録
        const timeSheetName = currentTeam + "_売上・時間当たり売上高管理表_" + month;
        let timeSheet = spreadsheet.getSheetByName(timeSheetName);
        if (!timeSheet) {
          timeSheet = spreadsheet.insertSheet(timeSheetName);
        }
        
        // 売上・時間当たり売上高管理表で日付の行を探す
        const data = timeSheet.getDataRange().getValues();
        let dayRow = -1;
        
        // A列で日付を検索
        for (let i = 0; i < data.length; i++) {
          if (data[i][0] === day) {
            dayRow = i + 1; // 1ベースの行番号
            break;
          }
        }
        
        // 日付の行が見つからない場合は新規追加
        if (dayRow === -1) {
          const lastRow = timeSheet.getLastRow() + 1;
          timeSheet.getRange("A" + lastRow).setValue(day);
          dayRow = lastRow;
        }
        
        // 件数に応じた列に記録
        const itemNumber = parseInt(tempSheet.getRange("C1").getValue().charCodeAt(0) - 65); // B=1, D=2, F=3, H=4から件数を逆算
        const actualItemNumber = (itemNumber + 1) / 2; // 1件目=1, 2件目=2, 3件目=3, 4件目=4
        const salesColumn = String.fromCharCode(65 + actualItemNumber * 2 - 1); // B, D, F, H
        const timeColumn = String.fromCharCode(65 + actualItemNumber * 2);      // C, E, G, I
        
        // 売上金額と稼働時間を記録
        timeSheet.getRange(salesColumn + dayRow).setValue(parseInt(salesAmount));
        timeSheet.getRange(timeColumn + dayRow).setValue(parseInt(userMessage));
        
        // フラグをクリア
        tempSheet.getRange("C1:E1").clearContent();
        tempSheet.getRange("G1").clearContent();
        
        // 完了メッセージを返信
        const url = 'https://api.line.me/v2/bot/message/reply';
        UrlFetchApp.fetch(url, {
          'headers': {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
          },
          'method': 'post',
          'payload': JSON.stringify({
            'replyToken': replyToken,
            'messages': [
              {
                'type': 'text',
                'text': salesType + '売上記録完了しました。\n売上: ' + salesAmount + '円、稼働時間: ' + userMessage + '分',
              }
            ]
          })
        });
      }
    }
  }
  
  // その他のメッセージは無視
  
  return ContentService.createTextOutput(JSON.stringify({ 'content': 'post ok' })).setMimeType(ContentService.MimeType.JSON);
}