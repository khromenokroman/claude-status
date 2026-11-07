// Claude Code Limits Indicator для GNOME Shell 45+
// Показывает процент использования лимитов в панели,
// при клике раскрывается меню с деталями.

import * as Extension from 'resource:///org/gnome/shell/extensions/extension.js';

const {GObject, GLib, St} = imports.gi;
const Main = imports.ui.main;
const PanelMenu = imports.ui.panelMenu;
const IndicatorBase = imports.indicators.indicator.IndicatorBase;

const SCRIPT_PATH = GLib.build_filenamev([
    GLib.get_user_config_dir(),
    'claude-status',
    'claude_usage.py'
]);

function parseIsoUtc(ts) {
    if (!ts)
        return null;
    try {
        const dt = new Date(ts);
        if (isNaN(dt.getTime()))
            return null;
        return dt.getTime() / 1000.0;
    } catch {
        return null;
    }
}

function formatCountdown(resetsAt) {
    const epoch = parseIsoUtc(resetsAt);
    if (epoch === null)
        return '';
    const remaining = Math.max(0, Math.floor(epoch - Date.now() / 1000.0));
    if (remaining <= 0)
        return 'сейчас';
    const h = Math.floor(remaining / 3600);
    const m = Math.floor((remaining % 3600) / 60);
    const s = remaining % 60;
    if (h > 0)
        return `${h}ч ${m}м`;
    if (m > 0)
        return `${m}м ${s}с`;
    return `${s}с`;
}

function formatLimitLine(label, utilization, resetsAt) {
    if (utilization === null || utilization === undefined)
        return '';
    const pct = Math.round(utilization);
    const countdown = formatCountdown(resetsAt);
    const cd = countdown ? `, сброс через ${countdown}` : '';
    return `${label}: ${pct}%${cd}`;
}

function buildTooltip(data) {
    if (!data || !data.ok) {
        return 'Claude Code: данные недоступны';
    }
    const lines = [];
    if (data.plan)
        lines.push(`План: ${data.plan}`);
    if (data.five_hour)
        lines.push(formatLimitLine('5ч окно', data.five_hour.utilization, data.five_hour.resets_at));
    if (data.seven_day)
        lines.push(formatLimitLine('7д окно', data.seven_day.utilization, data.seven_day.resets_at));
    return lines.join('\n') || 'Claude Code: данных нет';
}

function runPython(callback) {
    try {
        const result = GLib.spawn_command_line_sync(`python3 ${SCRIPT_PATH}`);
        const success = result[0];
        const stdout = new TextDecoder().decode(result[1]);
        const stderr = new TextDecoder().decode(result[2]);
        if (!success) {
            callback(null, `python3: ${stderr.trim()}`);
        } else {
            const data = JSON.parse(stdout);
            callback(data, null);
        }
    } catch (e) {
        callback(null, e.message);
    }
}

class ClaudeStatusIndicator extends IndicatorBase {
    constructor() {
        super('claude-status', 'claude-status-symbolic.svg');
        this._label = new St.Label({ text: 'CC' });
        this._menu = new PanelMenu.PanelMenu(this._label);
        Main.panel.addToStatusArea('claudeStatus', this, 100);

        this._header = this._menu.addMenuItem(new St.Label({
            text: 'Claude Code',
            style_class: 'panel-label',
        }));

        this._line1 = this._menu.addMenuItem(new St.Label({ text: 'загрузка…' }));
        this._line2 = this._menu.addMenuItem(new St.Label({ text: '' }));
        this._statusLine = this._menu.addMenuItem(new St.Label({ text: '' }));

        this._timer = null;
        this._start();
    }

    _start() {
        this._refresh();
        this._timer = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 60, () => {
            this._refresh();
            return GLib.SOURCE_CONTINUE;
        });
    }

    _refresh() {
        runPython((data, error) => {
            if (error) {
                this._label.set_text('CC');
                this._line1.set_text('Ошибка');
                this._line2.set_text(error);
                this._statusLine.set_text('');
                return;
            }
            if (!data || !data.ok) {
                this._label.set_text('CC');
                this._line1.set_text('Нет данных');
                this._line2.set_text(data?.error || 'неизвестная ошибка');
                this._statusLine.set_text('');
                return;
            }

            // Основной текст на панели: процент недельного окна
            const weekly = data.seven_day;
            if (weekly && weekly.utilization !== null) {
                this._label.set_text(`${Math.round(weekly.utilization)}%`);
            } else {
                this._label.set_text('CC');
            }

            this._line1.set_text(
                formatLimitLine('5ч окно', data.five_hour?.utilization, data.five_hour?.resets_at)
            );
            this._line2.set_text(
                formatLimitLine('7д окно', data.seven_day?.utilization, data.seven_day?.resets_at)
            );

            // Строка статуса (severity)
            const activeLimit = (data.limits || []).find(l => l.is_active);
            if (activeLimit) {
                const severity = activeLimit.severity || 'normal';
                const color = severity === 'critical' ? '#ff5555' :
                              severity === 'warning' ? '#ffaa00' : '#88ff88';
                this._statusLine.set_markup(
                    `<span foreground="${color}">Активный лимит: ${activeLimit.kind} (${activeLimit.percent}%)</span>`
                );
            } else {
                this._statusLine.set_text('');
            }
        });
    }

    destroy() {
        if (this._timer)
            GLib.source_remove(this._timer);
        this._menu.destroy();
        this._label.destroy();
        super.destroy();
    }
}

export default class ClaudeStatusExtension extends Extension.Extension {
    constructor(...args) {
        super(...args);
        this._indicator = null;
    }

    enable() {
        this._indicator = new ClaudeStatusIndicator();
    }

    disable() {
        if (this._indicator) {
            this._indicator.destroy();
            this._indicator = null;
        }
    }
}
