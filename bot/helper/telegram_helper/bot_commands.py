from bot import CMD_SUFFIX


class _BotCommands:
    def __init__(self):
        self.StartCommand = 'start'
        self.MirrorCommand = f'mirror{CMD_SUFFIX}'
        self.QbMirrorCommand = f'qbmirror{CMD_SUFFIX}'
        self.YtdlCommand = f'ytdl{CMD_SUFFIX}'
        self.LeechCommand = f'leech{CMD_SUFFIX}'
        self.QbLeechCommand = f'qbleech{CMD_SUFFIX}'
        self.YtdlLeechCommand = f'ytdlleech{CMD_SUFFIX}'
        self.CloneCommand = f'clone{CMD_SUFFIX}'
        self.CountCommand = f'count{CMD_SUFFIX}'
        self.DeleteCommand = f'del{CMD_SUFFIX}'
        self.CancelMirror = f'stop'
        self.CancelAllCommand = f'abort'
        self.ListCommand = f'find{CMD_SUFFIX}'
        self.SearchCommand = f'search{CMD_SUFFIX}'
        self.StatusCommand = f'status{CMD_SUFFIX}'
        self.UsersCommand = f'allow'
        self.AuthorizeCommand = f'auth'
        self.UnAuthorizeCommand = f'unauth'
        self.AddSudoCommand = f'addsudo'
        self.RmSudoCommand = f'unsudo'
        self.PingCommand = f'ping'
        self.RestartCommand = f'reboot'
        self.StatsCommand = f'usage'
        self.HelpCommand = f'help'
        self.LogCommand = f'log{CMD_SUFFIX}'
        
        self.ShellCommand = f'shellx{CMD_SUFFIX}'
        self.EvalCommand = f'evalx{CMD_SUFFIX}'
        self.ExecCommand = f'execx{CMD_SUFFIX}'
        self.ClearLocalsCommand = f'clearlocalsx{CMD_SUFFIX}'
        self.BotSetCommand = f'bsettingx{CMD_SUFFIX}'
        self.UserSetCommand = f'usettingx{CMD_SUFFIX}'
        self.BtSelectCommand = f'btselx{CMD_SUFFIX}'
        self.RssCommand = f'rssx{CMD_SUFFIX}'
        self.CategorySelect = f'catselx{CMD_SUFFIX}'
        self.RmdbCommand = f'rmdbx{CMD_SUFFIX}'


BotCommands = _BotCommands()
