import logging
from typing import Dict
from dataclasses import dataclass
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from telegram.constants import ParseMode

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен вашего бота
TOKEN = "8549510411:AAEvNul_wBcIMUbzTCArQ6EPSptlGNfN30M"

# Состояния
(
    MAIN_MENU, 
    PRODUCTS, 
    PAYMENT_METHOD,
    DELIVERY_METHOD,
    CONFIRMATION
) = range(5)

# Класс для товара
@dataclass
class Product:
    id: int
    name: str
    description: str
    price: float
    category: str = "general"

# База данных товаров
products_db = {
    1: Product(1, "💊ZEAL", "снюс со вкусом cola,200mg,16 паков", 599, "snus"),
    2: Product(2, "💊NAS", "снюс со вкусом malina,200mg,12 паков", 379, "snus"),
    3: Product(3, "💊NAS", "снюс со вкусом mint,200mg,12 паков", 379, "electronics"),
    4: Product(4, "💊YOVO", "снюс со вкусом JUCIY,200mg,15 паков", 400, "electronics"),
    5: Product(5, "💊PUCKER", "снюс со вкусом cherry,150mg,16 паков", 399, "electronics"),
    6: Product(6, "💊SNAX", "снюс со вкусом coffe,200mg,12 паков", 450, "electronics"),
}

# Хранилище заказов пользователей
user_orders: Dict[int, Dict] = {}

# ========== КЛАВИАТУРЫ ==========

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Создает главное меню"""
    keyboard = [
        [InlineKeyboardButton("🛍️ Перейти к покупке", callback_data='buy')],
        [InlineKeyboardButton("📞 Поддержка", callback_data='support')],
        [InlineKeyboardButton("ℹ️ О нас", callback_data='about')],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_products_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру с товарами"""
    keyboard = []
    
    for product in products_db.values():
        keyboard.append([
            InlineKeyboardButton(
                f"{product.name} - 🇷🇺{product.price:.2f}",
                callback_data=f'buy_product_{product.id}'
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🏠 В главное меню", callback_data='main_menu')])
    
    return InlineKeyboardMarkup(keyboard)

def get_payment_method_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора способа оплаты"""
    keyboard = [
        [InlineKeyboardButton("💳 Через FunPay", callback_data='payment_funpay')],
        [InlineKeyboardButton("🎁 Через подарки в ТГ", callback_data='payment_tg')],
        [InlineKeyboardButton("💵 Наличкой", callback_data='payment_cash')],
        [InlineKeyboardButton("🔙 Назад к товарам", callback_data='buy')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='main_menu')],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_delivery_method_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора способа получения"""
    keyboard = [
        [InlineKeyboardButton("🎭 Забрать анонимно", callback_data='delivery_anon')],
        [InlineKeyboardButton("👤 Забрать лично", callback_data='delivery_personal')],
        [InlineKeyboardButton("🔙 Назад к оплате", callback_data='back_to_payment')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='main_menu')],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения заказа"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить заказ", callback_data='confirm_order'),
            InlineKeyboardButton("❌ Отменить", callback_data='cancel_order')
        ],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='main_menu')],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_support_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для поддержки"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ К покупкам", callback_data='buy')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='main_menu')]
    ])

def get_about_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для информации о нас"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ К покупкам", callback_data='buy')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='main_menu')]
    ])

# ========== СООБЩЕНИЯ ==========

async def send_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение"""
    welcome_text = """
 *Добро пожаловать в наш магазин!* 

 *Главное* — быстро, надежно, анонимно!

 *Процесс покупки:*
1. Выберите товар
2. Выберите способ оплаты
3. Выберите способ получения
4. Подтвердите заказ

👇 *Начните покупки:*
    """
    
    if update.message:
        await update.message.reply_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.callback_query.edit_message_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    return MAIN_MENU

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает товары"""
    query = update.callback_query
    await query.answer()
    
    products_text = """
🛍️ *Выберите товар для покупки*

*Доступные товары:*
👇 *Нажмите на товар для продолжения:*
    """
    
    await query.edit_message_text(
        products_text,
        reply_markup=get_products_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
    
    return PRODUCTS

async def select_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор товара и сразу переходит к оплате"""
    query = update.callback_query
    await query.answer()
    
    # Извлекаем ID товара
    product_id = int(query.data.replace('buy_product_', ''))
    product = products_db.get(product_id)
    
    if not product:
        await query.edit_message_text("❌ Товар не найден!")
        return PRODUCTS
    
    # Сохраняем выбранный товар
    context.user_data['selected_product'] = product_id
    context.user_data['product_name'] = product.name
    context.user_data['product_price'] = product.price
    
    # Сразу переходим к выбору способа оплаты
    payment_text = f"""
💰 *Оплата*

*Выбран товар:*
**{product.name}**
Цена: `🇷🇺{product.price:.2f}`

👇 *Выберите способ оплаты:*
    """
    
    await query.edit_message_text(
        payment_text,
        reply_markup=get_payment_method_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
    
    return PAYMENT_METHOD

async def select_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор способа оплаты"""
    query = update.callback_query
    await query.answer()
    
    payment_method = query.data.replace('payment_', '')
    
    # Сохраняем выбранный способ оплаты
    context.user_data['payment_method'] = payment_method
    
    # Получаем информацию о товаре
    product_id = context.user_data.get('selected_product')
    product_name = context.user_data.get('product_name', 'Товар')
    product_price = context.user_data.get('product_price', 0)
    
    # Описание способов оплаты
    payment_methods_info = {
        'funpay': "💳 *FunPay* — безопасная оплата картой или криптовалютой",
        'tg': "🎁 *Подарки в Telegram* — отправьте подарок на наш аккаунт",
        'cash': "💵 *Наличные* — оплата при получении товара"
    }
    
    delivery_text = f"""
🚚 *Получение товара*

*Детали заказа:*
• Товар: **{product_name}**
• Цена: `🇷🇺{product_price:.2f}`
• Оплата: {payment_methods_info.get(payment_method, 'Не выбрано')}

👇 *Выберите способ получения:*
    """
    
    await query.edit_message_text(
        delivery_text,
        reply_markup=get_delivery_method_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
    
    return DELIVERY_METHOD

async def select_delivery_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор способа получения"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'back_to_payment':
        # Возвращаемся к выбору оплаты
        product_id = context.user_data.get('selected_product')
        product = products_db.get(product_id) if product_id else None
        
        if product:
            payment_text = f"""
💰 *Оплата*

*Выбран товар:*
**{product.name}**
Цена: `🇷🇺{product.price:.2f}`

👇 *Выберите способ оплаты:*
            """
            
            await query.edit_message_text(
                payment_text,
                reply_markup=get_payment_method_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
            return PAYMENT_METHOD
    
    delivery_method = query.data.replace('delivery_', '')
    
    # Сохраняем выбранный способ получения
    context.user_data['delivery_method'] = delivery_method
    
    # Получаем информацию о заказе
    product_name = context.user_data.get('product_name', 'Товар')
    product_price = context.user_data.get('product_price', 0)
    payment_method = context.user_data.get('payment_method', 'не выбран')
    
    # Информация о способах получения
    delivery_info = {
        'anon': "🎭 *Забрать анонимно* — встреча в нейтральном месте без обмена личными данными",
        'personal': "👤 *Забрать лично* — встреча с продавцом, возможен обмен контактами"
    }
    
    # Информация о способах оплаты
    payment_info = {
        'funpay': "💳 Через FunPay",
        'tg': "🎁 Через подарки в Telegram",
        'cash': "💵 Наличными"
    }.get(payment_method, "не указан")
    
    order_summary = f"""
📋 *Подтверждение заказа*

*Детали заказа:*
• **Товар:** {product_name}
• **Цена:** `🇷🇺{product_price:.2f}`
• **Оплата:** {payment_info}
• **Получение:** {delivery_info.get(delivery_method, 'не выбрано')}

👇 *Подтвердите заказ:*
    """
    
    await query.edit_message_text(
        order_summary,
        reply_markup=get_confirmation_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
    
    return CONFIRMATION

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение заказа"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'cancel_order':
        await query.edit_message_text(
            "❌ *Заказ отменен*\n\nВы можете вернуться к покупкам в любое время.",
            reply_markup=get_main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return MAIN_MENU
    
    # Получаем данные заказа
    product_id = context.user_data.get('selected_product')
    product = products_db.get(product_id) if product_id else None
    product_name = context.user_data.get('product_name', 'Товар')
    product_price = context.user_data.get('product_price', 0)
    payment_method = context.user_data.get('payment_method', 'не выбран')
    delivery_method = context.user_data.get('delivery_method', 'не выбран')
    
    if not product:
        await query.edit_message_text("❌ Ошибка при оформлении заказа")
        return MAIN_MENU
    
    user_id = query.from_user.id
    
    # Генерируем номер заказа
    order_id = f"ORD{user_id}{product_id}{len(user_orders)+1:03d}"
    
    # Сохраняем заказ
    user_orders[user_id] = {
        'order_id': order_id,
        'product_id': product_id,
        'product_name': product_name,
        'price': product_price,
        'payment_method': payment_method,
        'delivery_method': delivery_method,
        'status': 'в обработке'
    }
    
    # Сначала отправляем сообщение "ожидайте"
    await query.edit_message_text(
        "⏳ *Ожидайте в течение 10-15 минут, вам ответят*",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Ждем 2 секунды для визуального эффекта
    import asyncio
    await asyncio.sleep(2)
    
    # Теперь отправляем полную информацию о заказе
    # Инструкция в зависимости от способа оплаты
    payment_instructions = {
        'funpay': f"""
💳 *Инструкция по оплате через FunPay:*

📋 *Номер вашего заказа:* `{order_id}`

*Действия:*
1. Перейдите на: `funpay.ru/users/ваш_аккаунт/`
2. Сумма к оплате: `🇷🇺{product_price:.2f}`
3. После оплаты пришлите скриншот в этот чат
4. Ожидайте координаты встречи (10-15 минут)

📞 *Поддержка:* @ваша_поддержка
        """,
        'tg': f"""
🎁 *Инструкция по оплате подарками в Telegram:*

📋 *Номер вашего заказа:* `{order_id}`

*Действия:*
1. Отправьте подарок на: `@ваш_аккаунт`
2. Стоимость подарка: `🇷🇺{product_price:.2f}`
3. После отправки пришлите скриншот сюда
4. Ожидайте координаты встречи (10-15 минут)

📞 *Поддержка:* @ваша_поддержка
        """,
        'cash': f"""
💵 *Инструкция по оплате наличными:*

📋 *Номер вашего заказа:* `{order_id}`

*Действия:*
1. Сохраните номер заказа выше
2. Ожидайте координаты встречи (10-15 минут)
3. При встрече скажите кодовое слово: `СТИЛЬ{product_id}`
4. Оплата при получении: `${product_price:.2f}`

📞 *Поддержка:* @ваша_поддержка
        """
    }
    
    instruction = payment_instructions.get(payment_method, 
        f"📋 *Номер вашего заказа:* `{order_id}`\n\nОплатите `${product_price:.2f}` и пришлите подтверждение в этот чат.")
    
    success_text = f"""
✅ *Заказ успешно оформлен!*

📋 *Детали заказа:*
• Номер заказа: `{order_id}`
• Товар: {product_name}
• Сумма: `${product_price:.2f}`
• Статус: ⏳ *В обработке*

{instruction}

⏰ *Время ответа:* 10-15 минут
📍 *Место встречи:* Получите после оплаты

*Благодарим за покупку!*
    """
    
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=success_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Очищаем данные пользователя
    context.user_data.clear()
    
    return MAIN_MENU

async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает поддержку"""
    query = update.callback_query
    await query.answer()
    
    support_text = """
📞 *Поддержка*
@narkis1 - по всем вопросам писать сюда



    """
    
    await query.edit_message_text(
        support_text,
        reply_markup=get_support_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает информацию о нас"""
    query = update.callback_query
    await query.answer()
    
    about_text = """
При покупки вы автоматически принимаете все условия анонимности бота
А так же люблю Ачинский Кадетский Корпус который дал мне такую возможность продавать.
    """
    
    await query.edit_message_text(
        about_text,
        reply_markup=get_about_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

# ========== ОСНОВНОЙ КОД ==========

def main():
    """Запускает бота"""
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Создаем ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', send_welcome)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(show_products, pattern='^buy$'),
                CallbackQueryHandler(show_support, pattern='^support$'),
                CallbackQueryHandler(show_about, pattern='^about$'),
            ],
            PRODUCTS: [
                CallbackQueryHandler(select_product, pattern='^buy_product_'),
                CallbackQueryHandler(send_welcome, pattern='^main_menu$'),
                CallbackQueryHandler(show_products, pattern='^buy$'),
            ],
            PAYMENT_METHOD: [
                CallbackQueryHandler(select_payment_method, pattern='^payment_'),
                CallbackQueryHandler(show_products, pattern='^buy$'),
                CallbackQueryHandler(send_welcome, pattern='^main_menu$'),
            ],
            DELIVERY_METHOD: [
                CallbackQueryHandler(select_delivery_method, pattern='^delivery_'),
                CallbackQueryHandler(select_delivery_method, pattern='^back_to_payment$'),
                CallbackQueryHandler(send_welcome, pattern='^main_menu$'),
            ],
            CONFIRMATION: [
                CallbackQueryHandler(confirm_order, pattern='^(confirm_order|cancel_order)$'),
                CallbackQueryHandler(send_welcome, pattern='^main_menu$'),
            ],
        },
        fallbacks=[CommandHandler('start', send_welcome)],
    )
    
    # Добавляем обработчики
    application.add_handler(conv_handler)
    
    # Обработчик команды /help
    application.add_handler(CommandHandler('help', send_welcome))
    
    # Запускаем бота
    print("=" * 50)
    print("🤖 БОТ ЗАПУЩЕН!")
    print("=" * 50)
    print("📱 Процесс покупки:")
    print("1. Нажмите '🛍️ Перейти к покупке'")
    print("2. Выберите товар → переход к оплате")
    print("3. Выберите способ оплаты")
    print("4. Выберите способ получения")
    print("5. Подтвердите заказ")
    print("6. ⏰ Получите сообщение 'Ожидайте 10-15 минут'")
    print("7. Получите инструкции по оплате")
    print("=" * 50)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
