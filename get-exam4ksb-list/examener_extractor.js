/**
 * 考试宝题目提取脚本（逐题翻页版 + 5字体解混淆）
 * DOM结构：
 *   题目：div.qusetion-title
 *   选项容器：div.options-w
 *   正确答案：div.option.right（多选题有多个）
 *   字体混淆：根据元素的font-family样式选择对应映射表
 *   已收录5个混淆字体映射表
 *
 * 使用：F12 → Console 粘贴运行
 * 抽样模式：每种题型提取20道，验证后改为全量
 */
(async function() {
  'use strict';

  // ===== 5个混淆字体解混淆映射表 =====
  var FONT_MAPS = {
    "k1cc4fe88829c6f54890b351a11efda03": {"业": "员", "丝": "了", "主": "跳", "丽": "每", "举": "付", "么": "故", "习": "曾", "买": "待", "了": "丝", "云": "眼", "他": "工", "付": "举", "以": "怎", "伙": "免", "位": "杂", "作": "议", "依": "春", "便": "您", "信": "困", "光": "尽", "免": "伙", "全": "缺", "兰": "挥", "关": "喊", "况": "笑", "冷": "校", "则": "阵", "判": "禁", "到": "理", "前": "温", "加": "显", "南": "型", "发": "归", "口": "松", "古": "斗", "另": "火", "史": "常", "吃": "时", "吧": "脑", "告": "块", "员": "业", "味": "回", "呼": "醒", "啊": "张", "喊": "关", "喝": "奖", "回": "味", "困": "信", "在": "电", "坏": "集", "块": "告", "型": "南", "堂": "恋", "复": "月", "外": "收", "多": "际", "失": "课", "奖": "喝", "好": "选", "委": "险", "客": "西", "家": "鲜", "导": "康", "小": "营", "尼": "究", "尽": "光", "工": "他", "已": "间", "巴": "那", "希": "素", "帮": "早", "常": "史", "并": "摇", "康": "导", "张": "啊", "归": "发", "征": "误", "待": "买", "微": "答", "怎": "以", "思": "散", "性": "继", "恋": "堂", "您": "便", "所": "降", "找": "是", "担": "朋", "拉": "顿", "拥": "见", "挥": "兰", "提": "病", "摇": "并", "收": "外", "改": "模", "故": "么", "散": "思", "斗": "古", "斯": "赶", "早": "帮", "时": "吃", "春": "依", "是": "找", "显": "加", "曾": "习", "月": "复", "朋": "担", "术": "绝", "杂": "位", "李": "饭", "束": "章", "条": "演", "松": "口", "某": "步", "树": "食", "校": "冷", "模": "改", "步": "某", "每": "丽", "毕": "诺", "求": "深", "沙": "静", "波": "窗", "泪": "闻", "深": "求", "温": "前", "演": "条", "火": "另", "灵": "热", "热": "灵", "然": "碃", "现": "祖", "理": "到", "电": "在", "病": "提", "直": "赛", "看": "职", "眼": "云", "碃": "然", "祖": "现", "禁": "判", "称": "迹", "究": "尼", "穿": "立", "窗": "波", "立": "穿", "章": "束", "笑": "况", "答": "微", "简": "雄", "素": "希", "绝": "术", "继": "性", "缺": "全", "职": "看", "联": "警", "肯": "释", "脑": "吧", "英": "血", "菜": "雨", "营": "小", "血": "英", "西": "客", "见": "拥", "视": "这", "諣": "说", "警": "联", "议": "作", "诗": "项", "误": "征", "说": "諣", "诺": "毕", "课": "失", "赛": "直", "赶": "斯", "跳": "主", "这": "视", "迹": "称", "送": "高", "选": "好", "那": "巴", "醒": "呼", "释": "肯", "间": "已", "闻": "泪", "阳": "露", "阵": "则", "际": "多", "降": "所", "险": "委", "雄": "简", "集": "坏", "雨": "菜", "露": "阳", "静": "沙", "项": "诗", "顿": "拉", "食": "树", "饭": "李", "高": "送", "鲜": "家"},
    "k4e047354e1bd143c4d67bd60b218ab60": {"万": "通", "下": "商", "中": "尽", "久": "土", "么": "笑", "乐": "新", "乡": "月", "争": "慢", "些": "困", "亡": "注", "人": "价", "介": "吗", "仍": "好", "以": "另", "价": "人", "任": "毛", "份": "顺", "众": "律", "伦": "阳", "伯": "己", "余": "过", "便": "既", "保": "食", "值": "角", "做": "鲜", "健": "孩", "光": "格", "入": "桌", "八": "抱", "其": "坚", "决": "我", "击": "而", "列": "女", "刘": "周", "别": "象", "十": "酒", "千": "母", "升": "毫", "却": "历", "历": "却", "及": "宣", "反": "究", "古": "店", "另": "以", "叫": "读", "右": "纸", "各": "虽", "合": "授", "后": "士", "吗": "介", "含": "民", "周": "刘", "商": "下", "因": "负", "困": "些", "土": "久", "坏": "感", "坐": "诗", "坚": "其", "堂": "妈", "士": "后", "套": "念", "奥": "改", "女": "列", "好": "仍", "妈": "堂", "始": "尼", "娘": "议", "娜": "青", "存": "领", "孩": "健", "宣": "及", "寻": "烈", "尼": "始", "尽": "中", "属": "英", "己": "伯", "店": "古", "式": "易", "影": "熟", "律": "众", "微": "终", "忙": "拍", "快": "论", "念": "套", "怎": "迹", "怪": "苏", "息": "立", "悲": "职", "惊": "编", "感": "坏", "慢": "争", "懂": "挥", "我": "决", "护": "森", "抱": "八", "拍": "忙", "按": "自", "挥": "懂", "授": "合", "探": "类", "支": "流", "收": "树", "改": "奥", "数": "村", "断": "画", "新": "乐", "既": "便", "旧": "珍", "易": "式", "春": "武", "是": "船", "晚": "跟", "更": "这", "月": "乡", "权": "饭", "村": "数", "来": "造", "林": "讲", "标": "秋", "树": "收", "格": "光", "桌": "入", "森": "护", "次": "轻", "正": "须", "武": "春", "母": "千", "毛": "任", "毫": "升", "民": "含", "波": "达", "注": "亡", "流": "支", "火": "进", "烈": "寻", "熟": "影", "牙": "留", "状": "鲁", "珍": "旧", "画": "断", "留": "牙", "百": "福", "相": "种", "确": "背", "社": "际", "禁": "育", "福": "百", "秋": "标", "种": "相", "究": "反", "立": "息", "笑": "么", "类": "探", "纸": "右", "终": "微", "编": "惊", "而": "击", "职": "悲", "育": "禁", "背": "确", "自": "按", "船": "是", "苏": "怪", "虽": "各", "蜖": "难", "角": "值", "议": "娘", "讲": "林", "论": "快", "诗": "坐", "读": "叫", "象": "别", "负": "因", "赛": "飞", "跟": "晚", "轻": "次", "达": "波", "过": "余", "这": "更", "进": "火", "迹": "怎", "送": "需", "通": "万", "造": "来", "酒": "十", "阳": "伦", "际": "社", "难": "蜖", "需": "送", "青": "娜", "顺": "份", "须": "正", "领": "存", "飞": "赛", "食": "保", "饭": "权", "鲁": "状", "鲜": "做"},
    "kc75b73e04abd0cd18fc2ebdb2c4240b6": {"一": "伊", "万": "口", "三": "精", "上": "白", "下": "药", "业": "悲", "严": "比", "丽": "回", "义": "海", "乐": "座", "乡": "员", "事": "线", "五": "费", "交": "公", "从": "封", "付": "它", "令": "职", "伊": "一", "优": "多", "会": "律", "传": "围", "似": "题", "低": "纸", "供": "统", "像": "怪", "全": "哥", "八": "凡", "公": "交", "兵": "冰", "内": "黄", "写": "学", "冰": "兵", "决": "相", "凡": "八", "动": "察", "千": "萨", "午": "次", "华": "钱", "卖": "失", "又": "牌", "双": "简", "反": "引", "受": "甚", "口": "万", "右": "误", "吉": "提", "员": "乡", "哥": "全", "哪": "据", "商": "需", "喜": "段", "器": "续", "四": "骨", "回": "丽", "因": "法", "团": "害", "围": "传", "场": "须", "坐": "忘", "坦": "岛", "境": "获", "声": "运", "多": "优", "夜": "秘", "失": "卖", "奥": "请", "妹": "认", "婚": "组", "子": "换", "学": "写", "它": "付", "守": "感", "害": "团", "容": "确", "察": "动", "封": "从", "小": "并", "少": "洋", "山": "石", "岛": "坦", "带": "质", "并": "小", "座": "乐", "庭": "望", "引": "反", "征": "竟", "律": "会", "忘": "坐", "性": "考", "怪": "像", "悲": "业", "感": "守", "戏": "武", "所": "拍", "找": "站", "护": "资", "拍": "所", "按": "者", "换": "子", "据": "哪", "接": "餐", "提": "吉", "散": "此", "斗": "话", "方": "远", "望": "庭", "条": "由", "松": "际", "树": "衣", "梦": "足", "次": "午", "此": "散", "武": "戏", "段": "喜", "比": "严", "法": "因", "洋": "少", "派": "言", "海": "义", "清": "穿", "火": "百", "然": "诺", "照": "脸", "牌": "又", "物": "素", "球": "论", "甚": "受", "由": "条", "电": "跳", "白": "上", "百": "火", "相": "决", "睛": "良", "石": "山", "确": "容", "离": "露", "秘": "夜", "穿": "清", "站": "找", "竟": "征", "笔": "过", "第": "背", "简": "双", "管": "戴", "精": "三", "素": "物", "纸": "低", "线": "事", "组": "婚", "结": "高", "统": "供", "续": "器", "编": "英", "考": "性", "者": "按", "职": "令", "背": "第", "脸": "照", "般": "装", "良": "睛", "色": "部", "英": "编", "药": "下", "获": "境", "萨": "千", "衣": "树", "装": "般", "言": "派", "警": "险", "认": "妹", "让": "飞", "论": "球", "话": "斗", "误": "右", "请": "奥", "诺": "然", "质": "带", "费": "五", "资": "护", "足": "梦", "跳": "电", "转": "醒", "过": "笔", "运": "声", "远": "方", "部": "色", "醒": "转", "钱": "华", "际": "松", "险": "警", "需": "商", "露": "离", "须": "场", "题": "似", "飞": "让", "餐": "接", "骨": "四", "高": "结", "黄": "内"},
    "kca7d9c360bb990cca7d2053ae35b2a7f": {"一": "福", "万": "双", "世": "碃", "业": "典", "东": "奶", "严": "组", "为": "恶", "也": "诗", "习": "更", "买": "展", "了": "片", "事": "景", "云": "对", "亮": "济", "介": "江", "他": "春", "代": "听", "众": "渐", "伴": "雪", "体": "自", "何": "范", "便": "喜", "做": "黑", "先": "能", "兴": "血", "典": "业", "再": "当", "冰": "雨", "分": "图", "刻": "语", "办": "新", "功": "际", "化": "姑", "医": "整", "十": "赶", "卫": "致", "即": "线", "及": "班", "双": "万", "取": "已", "吗": "数", "含": "听", "听": "含", "呢": "餐", "哪": "您", "哭": "楼", "商": "红", "善": "谁", "喜": "便", "回": "送", "图": "分", "场": "德", "坚": "请", "境": "极", "外": "火", "多": "非", "够": "抱", "头": "念", "奶": "东", "姑": "化", "学": "广", "宣": "此", "室": "秘", "对": "云", "尔": "法", "展": "买", "属": "样", "山": "纪", "巨": "蜖", "己": "置", "已": "取", "幸": "望", "广": "学", "店": "用", "引": "问", "当": "再", "德": "场", "念": "头", "怎": "排", "思": "牌", "性": "编", "恶": "为", "您": "哪", "慢": "断", "战": "解", "手": "早", "才": "贝", "托": "研", "找": "藏", "抱": "够", "排": "怎", "提": "级", "改": "汉", "数": "吗", "整": "医", "断": "慢", "新": "办", "旅": "质", "既": "超", "早": "手", "星": "露", "春": "他", "景": "事", "智": "泪", "更": "习", "望": "幸", "束": "进", "来": "祖", "极": "境", "桌": "索", "楼": "哭", "此": "宣", "毫": "读", "汉": "改", "江": "介", "沙": "罪", "油": "钱", "法": "尔", "泪": "智", "流": "缺", "济": "亮", "清": "青", "渐": "众", "火": "外", "烧": "说", "片": "了", "牌": "思", "状": "登", "班": "及", "用": "店", "登": "状", "真": "验", "研": "托", "碃": "世", "祖": "来", "福": "一", "秘": "室", "童": "觉", "答": "讲", "米": "细", "类": "顾", "索": "桌", "红": "商", "级": "提", "纪": "山", "线": "即", "组": "严", "细": "米", "续": "落", "编": "性", "缺": "流", "罪": "沙", "置": "己", "翻": "鲁", "考": "高", "能": "先", "自": "体", "致": "卫", "舞": "革", "范": "何", "落": "续", "藏": "找", "蜖": "巨", "血": "兴", "觉": "童", "解": "战", "讲": "答", "诗": "也", "语": "刻", "说": "烧", "请": "坚", "读": "毫", "谁": "善", "贝": "才", "质": "旅", "赶": "十", "超": "既", "路": "钟", "进": "束", "送": "回", "酒": "马", "钟": "路", "钱": "油", "问": "引", "际": "功", "雨": "冰", "雪": "伴", "露": "星", "青": "清", "非": "多", "革": "舞", "顾": "类", "餐": "呢", "马": "酒", "验": "真", "高": "考", "鲁": "翻", "黑": "做"},
    "k510cf9754ff36d34b446d7e01b4bf4da": {"万": "几", "三": "摇", "下": "把", "且": "典", "丝": "肉", "丽": "词", "久": "律", "么": "哭", "之": "良", "习": "风", "云": "够", "亚": "红", "亮": "旁", "仅": "底", "代": "牙", "价": "山", "任": "里", "伤": "释", "伦": "越", "住": "终", "体": "笑", "光": "男", "克": "记", "全": "器", "具": "着", "典": "且", "几": "万", "划": "村", "利": "紧", "制": "致", "功": "消", "化": "州", "北": "整", "区": "归", "升": "易", "午": "吉", "华": "英", "单": "梦", "即": "座", "历": "托", "原": "我", "口": "板", "古": "翻", "台": "权", "吉": "午", "呢": "油", "周": "定", "和": "提", "哭": "么", "唱": "童", "器": "全", "图": "艺", "坐": "安", "士": "队", "处": "数", "夏": "女", "够": "云", "套": "科", "女": "夏", "她": "觉", "好": "晚", "姑": "掉", "安": "坐", "定": "周", "属": "乐", "山": "价", "州": "化", "幸": "收", "广": "情", "床": "转", "底": "仅", "座": "即", "异": "找", "弟": "足", "归": "区", "录": "祖", "影": "月", "律": "久", "微": "犯", "心": "见", "思": "的", "情": "广", "我": "原", "打": "灯", "托": "历", "找": "异", "把": "下", "投": "草", "掉": "姑", "提": "和", "摇": "三", "收": "幸", "教": "道", "数": "处", "整": "北", "文": "面", "旁": "亮", "易": "升", "是": "近", "晚": "好", "月": "影", "未": "玩", "权": "台", "村": "划", "板": "口", "查": "缺", "梦": "单", "楼": "酒", "此": "银", "沙": "石", "油": "呢", "波": "识", "消": "功", "游": "跟", "灯": "打", "烟": "误", "熟": "顺", "牙": "代", "犯": "微", "玩": "未", "环": "白", "男": "光", "登": "育", "白": "环", "的": "思", "盖": "看", "看": "盖", "着": "具", "石": "沙", "研": "馆", "祖": "录", "票": "雄", "福": "苏", "科": "套", "称": "蜖", "究": "续", "童": "唱", "笑": "体", "素": "象", "紧": "利", "红": "亚", "终": "住", "经": "问", "绝": "继", "统": "钟", "继": "绝", "续": "究", "缺": "查", "翻": "古", "肉": "丝", "育": "登", "胜": "默", "胡": "鸟", "脱": "认", "致": "制", "良": "之", "艺": "图", "苏": "福", "英": "华", "草": "投", "蜖": "称", "衣": "装", "装": "衣", "见": "心", "觉": "她", "认": "脱", "记": "克", "识": "波", "词": "丽", "误": "烟", "课": "送", "谁": "鞋", "象": "素", "越": "伦", "足": "弟", "跟": "游", "转": "床", "运": "革", "近": "是", "追": "饭", "送": "课", "道": "教", "酒": "楼", "释": "伤", "里": "任", "钟": "统", "银": "此", "问": "经", "队": "士", "雄": "票", "面": "文", "革": "运", "鞋": "谁", "顺": "熟", "风": "习", "饭": "追", "馆": "研", "鸟": "胡", "默": "胜"}
  };

  // 获取元素的混淆字体名（从内联style或计算样式）
  function getObfuscatedFontFamily(el) {
    if (!el) return null;
    // 1. 优先从内联style获取
    var style = el.getAttribute('style') || '';
    var m = style.match(/font-family:\s*k([a-f0-9]+)/);
    if (m) return 'k' + m[1];
    // 2. 从计算样式获取
    var computed = getComputedStyle(el).fontFamily;
    var m2 = computed.match(/k([a-f0-9]+)/);
    if (m2) return 'k' + m2[1];
    // 3. 遍历子元素查找
    var children = el.querySelectorAll('*');
    for (var ci = 0; ci < Math.min(children.length, 10); ci++) {
      var cstyle = children[ci].getAttribute('style') || '';
      var cm = cstyle.match(/font-family:\s*k([a-f0-9]+)/);
      if (cm) return 'k' + cm[1];
    }
    return null;
  }

  // 根据字体映射表解码文本
  function decodeWithFont(text, fontKey) {
    var map = FONT_MAPS[fontKey];
    if (!map) return text;
    var result = '';
    for (var i = 0; i < text.length; i++) {
      var ch = text[i];
      result += map[ch] || ch;
    }
    return result;
  }

  // 智能解码：自动检测元素使用的字体并解码
  function smartDecode(el) {
    if (!el) return '';
    var text = el.innerText.replace(/\s+/g, ' ').trim();
    var fontKey = getObfuscatedFontFamily(el);
    if (fontKey && FONT_MAPS[fontKey]) {
      return decodeWithFont(text, fontKey);
    }
    // Fallback: 尝试所有映射表，优先选择能产生正确题型标记的
    for (var key in FONT_MAPS) {
      var decoded = decodeWithFont(text, key);
      if (/\[(单选题|多选题|判断题|填空题|简答题)\]/.test(decoded)) {
        return decoded;
      }
    }
    return text;
  }

  // ===== 全量模式：每种题型设为0表示不限 =====
  var SAMPLE_LIMIT = { '单选题': 0, '多选题': 0, '判断题': 0 };

  var DELAY_MS = 600;
  var MAX_QUESTIONS = 500;
  var results = [];
  var seenTexts = {};
  var questionCount = 0;
  var noNewCount = 0;
  var typeCount = {};

  var isSampleMode = false;
  for (var tk in SAMPLE_LIMIT) {
    if (SAMPLE_LIMIT[tk] > 0) { isSampleMode = true; break; }
  }

  console.log('\u{1F680} 考试宝提取脚本启动（5字体解混淆）...');
  console.log('\u{1F4DA} 已加载 ' + Object.keys(FONT_MAPS).length + ' 个字体映射表');
  if (isSampleMode) {
    console.log('\u{1F4CA} 抽样模式：' + JSON.stringify(SAMPLE_LIMIT));
  } else {
    console.log('\u{1F4CA} 全量模式');
  }

  function checkTypeDone(type) {
    if (!type || !isSampleMode) return false;
    if (!SAMPLE_LIMIT[type] || SAMPLE_LIMIT[type] === 0) return false;
    return (typeCount[type] || 0) >= SAMPLE_LIMIT[type];
  }

  function allTypesDone() {
    if (!isSampleMode) return false;
    for (var t in SAMPLE_LIMIT) {
      if (SAMPLE_LIMIT[t] > 0 && (typeCount[t] || 0) < SAMPLE_LIMIT[t]) return false;
    }
    return true;
  }

  function wait(ms) {
    return new Promise(function(r) { setTimeout(r, ms); });
  }

  // 提取当前页面题目
  function extractCurrentQuestion() {
    var q = { type: '', title: '', options: {}, answer: '', analysis: '' };

    // 题目文本：div.qusetion-title
    var titleEl = document.querySelector('div.qusetion-title');
    if (!titleEl) { titleEl = document.querySelector('div.question-title'); }

    if (titleEl) {
      q.title = smartDecode(titleEl);
      var m = q.title.match(/\[(单选题|多选题|判断题|填空题|简答题)\]/);
      if (m) q.type = m[1];
    }

    // 选项容器：div.options-w
    var optionsContainer = document.querySelector('div.options-w');
    if (optionsContainer) {
      var optEls = optionsContainer.querySelectorAll('div.option');
      for (var i = 0; i < optEls.length; i++) {
        var text = smartDecode(optEls[i]);
        var match = text.match(/^([A-Z])[、.．:：\s]\s*(.*)/);
        if (match) {
          q.options[match[1]] = match[2] || text.replace(/^[A-Z][、.．:：\s]\s*/, '');
        } else {
          var firstChar = text.charAt(0);
          if (/^[A-Z]$/.test(firstChar)) {
            q.options[firstChar] = text.substring(1).replace(/^[、.．:：\s]\s*/, '');
          }
        }
      }
    }

    // 正确答案：div.option.right（多选题会有多个）
    var rightEls = optionsContainer ? optionsContainer.querySelectorAll('div.option.right') : document.querySelectorAll('div.option.right');
    var answerParts = [];
    for (var ri = 0; ri < rightEls.length; ri++) {
      var rightText = smartDecode(rightEls[ri]);
      var m = rightText.match(/^([A-Z])/);
      if (m) {
        answerParts.push(m[1]);
      } else {
        answerParts.push(rightText);
      }
    }
    q.answer = answerParts.sort().join('');

    // 解析（如果有）
    var analysisEl = document.querySelector('div.analysis, div.explain, div[class*="analysis"], div[class*="jiexi"]');
    if (analysisEl) {
      q.analysis = smartDecode(analysisEl);
    }

    return q;
  }

  // 查找下一题按钮
  function findNextButton() {
    var btns = document.querySelectorAll('button, a, div[role="button"], span[role="button"], div.btn, span.btn');
    for (var i = 0; i < btns.length; i++) {
      var text = btns[i].innerText.replace(/\s+/g, ' ').trim();
      if (/^(下一题|下一页|下一个|next|继续)$/i.test(text)) {
        if (!btns[i].disabled) return btns[i];
      }
    }
    var nextEl = document.querySelector(
      '.next-btn, .btn-next, .next-question, ' +
      'div[class*="next"], a[class*="next"]'
    );
    if (nextEl && !nextEl.disabled) return nextEl;
    return null;
  }

  // ===== 主流程 =====
  var firstQ = extractCurrentQuestion();
  if (firstQ.title) {
    if (!checkTypeDone(firstQ.type)) {
      results.push(firstQ);
      seenTexts[firstQ.title] = true;
      typeCount[firstQ.type] = (typeCount[firstQ.type] || 0) + 1;
      questionCount++;
      console.log('\u{1F4DD} 第' + questionCount + '题 [' + firstQ.type + ' ' + (typeCount[firstQ.type]||0) + '/' + (SAMPLE_LIMIT[firstQ.type]||'\u221E') + ']: ' + firstQ.title.substring(0, 50));
    } else {
      console.log('\u23ED\uFE0F [' + firstQ.type + '] 已达抽样上限，跳过');
    }
  } else {
    console.log('\u26A0\uFE0F 未获取到题目，请确认页面结构');
  }

  while (questionCount < MAX_QUESTIONS && !allTypesDone()) {
    var nextBtn = findNextButton();

    if (!nextBtn) {
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', keyCode: 39 }));
      await wait(DELAY_MS);

      var q = extractCurrentQuestion();
      if (q.title && !seenTexts[q.title]) {
        seenTexts[q.title] = true;
        if (!checkTypeDone(q.type)) {
          results.push(q);
          typeCount[q.type] = (typeCount[q.type] || 0) + 1;
          questionCount++;
          noNewCount = 0;
          console.log('\u{1F4DD} 第' + questionCount + '题 [' + q.type + ' ' + typeCount[q.type] + '/' + (SAMPLE_LIMIT[q.type]||'\u221E') + ']: ' + q.title.substring(0, 50));
        } else {
          noNewCount = 0;
          console.log('\u23ED\uFE0F [' + q.type + '] 已达抽样上限，继续翻页...');
        }
      } else {
        noNewCount++;
        if (noNewCount >= 5) {
          console.log('\u2705 连续5次无新题，提取完成');
          break;
        }
      }
      continue;
    }

    nextBtn.click();
    await wait(DELAY_MS);

    var q = extractCurrentQuestion();

    if (q.title && !seenTexts[q.title]) {
      seenTexts[q.title] = true;
      if (!checkTypeDone(q.type)) {
        results.push(q);
        typeCount[q.type] = (typeCount[q.type] || 0) + 1;
        questionCount++;
        noNewCount = 0;
        console.log('\u{1F4DD} 第' + questionCount + '题 [' + q.type + ' ' + typeCount[q.type] + '/' + (SAMPLE_LIMIT[q.type]||'\u221E') + ']: ' + q.title.substring(0, 50));
      } else {
        noNewCount = 0;
        console.log('\u23ED\uFE0F [' + q.type + '] 已达抽样上限，继续翻页...');
      }
    } else {
      noNewCount++;
      if (noNewCount >= 5) {
        console.log('\u2705 连续5次无新题，可能已到最后一题');
        break;
      }
    }
  }

  if (allTypesDone()) {
    console.log('\n\u{1F3AF} 所有题型抽样完成！');
  }

  console.log('\n\u{1F389} 提取完成！共 ' + results.length + ' 道题');
  for (var t in typeCount) {
    console.log('  ' + t + ': ' + typeCount[t] + '道');
  }

  // 输出到控制台
  for (var i = 0; i < results.length; i++) {
    var q = results[i];
    console.log('\n【第' + (i + 1) + '题】' + q.type);
    console.log('题目：' + q.title);
    var keys = Object.keys(q.options);
    for (var j = 0; j < keys.length; j++) {
      console.log('  ' + keys[j] + '. ' + q.options[keys[j]]);
    }
    console.log('答案：' + q.answer);
    if (q.analysis) console.log('解析：' + q.analysis);
  }

  // 生成 Markdown
  var md = '# 考试宝题目提取结果\n\n';
  md += '提取时间：' + new Date().toLocaleString() + '\n';
  md += '来源：' + location.href + '\n';
  md += '共 ' + results.length + ' 道题\n\n---\n\n';

  for (var i = 0; i < results.length; i++) {
    var q = results[i];
    md += '## ' + (i + 1) + '. ';
    if (q.type) md += '（' + q.type + '）';
    md += q.title + '\n\n';
    var keys = Object.keys(q.options);
    for (var j = 0; j < keys.length; j++) {
      md += '- ' + keys[j] + '. ' + q.options[keys[j]] + '\n';
    }
    md += '\n**答案：' + (q.answer || '未获取') + '**\n\n';
    if (q.analysis) md += '**解析：**' + q.analysis + '\n\n';
    md += '---\n\n';
  }

  // 下载 JSON
  var jsonStr = JSON.stringify(results, null, 2);
  var blob1 = new Blob([jsonStr], { type: 'application/json' });
  var url1 = URL.createObjectURL(blob1);
  var a1 = document.createElement('a');
  a1.href = url1;
  a1.download = 'examener_' + Date.now() + '.json';
  a1.click();
  URL.revokeObjectURL(url1);

  // 下载 Markdown
  var blob2 = new Blob([md], { type: 'text/markdown' });
  var url2 = URL.createObjectURL(blob2);
  var a2 = document.createElement('a');
  a2.href = url2;
  a2.download = 'examener_' + Date.now() + '.md';
  a2.click();
  URL.revokeObjectURL(url2);

  console.log('\n\u{1F4E6} 已自动下载 JSON + Markdown 文件');
  window.__ksb_data = results;
  console.log('\u{1F4A1} 数据已保存到 window.__ksb_data');
})();
