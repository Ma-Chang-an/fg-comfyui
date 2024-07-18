import { api } from "/scripts/api.js";
import { app } from "/scripts/app.js";
import { $el } from "/scripts/ui.js";

$el("style", {
    textContent: `
    div.fg-alert-wrapper {
        position: absolute;
        background: var(--comfy-menu-bg);
        color: var(--fg-color);
        z-index: 99;
        font-family: sans-serif;
        font-size: 12px;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        top: 0;
        left: 0;
        right: 0;
        padding: 0.5em;
    }

    div.fg.title {

    }

    div.fg.description {
        flex: auto;
    }

    div.fg.description p {
        margin: 0;
        margin-bottom: 0.5em;
    }

    div.fg.button {
        margin: auto;
    }
    
	`,
    parent: document.body,
});


/**
 * 预估费用
 */
function calcCost(seconds) {
    return `${(seconds * 0.01475456).toFixed(2)} 元`
}

/**
 * 将秒转换为可读的时间
 */
function formatTime(seconds) {
    const unit = [["天", 86400], ["小时", 3600], ["分", 60], ["秒", 1]];
    let timeString = '';

    unit.forEach(([label, value]) => {
        if (seconds >= value) {
            const amount = Math.floor(seconds / value);
            seconds %= value;
            timeString += `${amount} ${label} `;
        }
    });

    return timeString.trim() || '0 秒';
}

app.registerExtension({
    name: "fg.alert",
    async setup() {
        const fgAlert = $el("div.fg-alert-wrapper");
        const timerShow = $el("p")

        const closeTime = 10 * 60;
        const documentTitle = document.title;
        let isNotInTab = false;

        let startTime = 0;
        let sleepTime = 0;
        window.__debug_set_sleep_time = (a) => sleepTime = a;

        const intervalId = setInterval(() => {
            timerShow.textContent = `当前页面已打开 ${formatTime(startTime)}，本次页面预计产生费用 ${calcCost(startTime)}（仅供参考，请以实际账单为准），距离上次主动操作（出图、切换页面）已 ${formatTime(sleepTime)}，将在 ${formatTime(closeTime - sleepTime)} 后自动关闭页面，以节省费用。`

            if (isNotInTab) {
                document.title = `ComfyUI 仍在消耗您的资源，将在 ${formatTime(closeTime - sleepTime)} 后自动关闭`
            } else if (document.title !== documentTitle) {
                document.title = documentTitle;
            }

            if (closeTime - sleepTime <= 0) {
                window.close();
                window.location.href = "about:blank"
                setTimeout(
                    () => {
                        alert("页面自动关闭失败，请手动关闭")
                    },
                    500
                )

            }

            startTime += 1;
            sleepTime += 1;
        }, 1000)

        fgAlert.append(
            $el("div.fg-title", [
                $el("b", {
                    textContent: "友情提示",
                    style: {
                        marginRight: "1em"
                    }
                }),
            ]),
            $el("div.fg.description", [
                $el("p", [
                    $el("span", {
                        textContent: "由于 ComfyUI 前端页面会不间断地发送HTTP请求以维持与服务器的连接，并且需要长久保持 WebSocket 连接以同步实时状态，这会导致函数弹性实例无法退出，因此页面打开时会持续使用计算资源。",
                    }),
                    $el("span", {
                        textContent: "即页面打开就会有费用产生！",
                        style: {
                            color: "red"
                        }
                    }),
                ]),
                timerShow,
                $el("p", { textContent: "由于首次出图需要加载模型，故会导致出图时间较长，请耐心等待；" }),
                $el("p", { textContent: "本页面内展示的模型、节点等均由第三方提供，FunctionGraph不对其所导致的不良结果或潜在风险承担任何责任，您需同意遵守第三方提出的各项要求，方可正式开启使用。" }),
            ]),
            $el("div.fg.button", [
                $el("button", {
                    onclick: (e) => {
                        sleepTime = 0;
                        fgAlert.style.display = "none";
                        clearInterval(intervalId);
                    },
                }, [
                    $el("span", { textContent: "我已理解费用问题" }),
                    $el("br"),
                    $el("span", { textContent: "本次使用关闭提醒" })
                ])
            ])
        );

        if (!fgAlert.parent) {
            document.body.append(fgAlert);
        }


        function resetSleepTime() {
            sleepTime = 0;
        }

        api.addEventListener("progress", resetSleepTime);
        api.addEventListener("executed", resetSleepTime);
        api.addEventListener("execution_start", resetSleepTime);
        api.addEventListener("execexecution_erroruted", resetSleepTime);
        api.addEventListener("execution_cached", resetSleepTime);

        document.addEventListener("mousemove", resetSleepTime);
        document.addEventListener("keydown", resetSleepTime);
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState == 'visible') {
                resetSleepTime();
                isNotInTab = false;
            } else if (document.visibilityState == 'hidden') {
                isNotInTab = true;
            }
        });
    },
});
