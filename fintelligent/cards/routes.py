from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from fintelligent.utils.decorators import tier_required

cards = Blueprint('cards', __name__)

@cards.route('/cards')
@login_required
@tier_required(['STUDENT', 'PRO'])
def compare_cards():
    """Render the credit card comparison page"""
    return render_template('cards.html')

@cards.route('/api/cards')
def get_cards_data():
    """API endpoint to get credit card comparison data with detailed points system (Indian context)"""
    cards_data = [
        {
            "name": "HDFC Infinia Credit Card",
            "best_for": "Premium, High Spenders",
            "rewards": "3.3% to 33%",
            "lounge": "Unlimited Domestic & International",
            "joining_fee": "₹12,500 + GST",
            "annual_fee": "₹12,500 + GST",
            "waiver": "₹10 Lakh annual spend",
            "key_benefit": "1:1 redemption on SmartBuy, points transfer to airline/hotel",
            "category": "Premium",
            "source": "https://www.cardmaven.in",
            "points_system": {
                "unit": "Reward Point (RP)",
                "cash_conversion": "1 RP = ₹0.30 (Statement Credit) | 1 RP = ₹1.00 (Apple/Tanishq on SmartBuy)",
                "flight_conversion": "1 RP = 1 Mile (Singapore Airlines, Air France/KLM, etc.) | 1 RP = 0.5 Mile (Air India, Etihad, etc.)",
                "hotel_conversion": "1 RP = 1 Point (IHG, Wyndham) | 1 RP = 0.5 Point (Accor, Marriott Bonvoy)",
                "redemption_portal": "HDFC SmartBuy / NetBanking",
                "where_to_use": "Best value (₹1) on SmartBuy for Flights/Hotels/Apple products. Good value for Air Miles transfer."
            }
        },
        {
            "name": "SBI Cashback Card",
            "best_for": "Online Shopping, Cashback",
            "rewards": "5% on online spends",
            "lounge": "N/A",
            "joining_fee": "₹999 + Taxes",
            "annual_fee": "₹999 + Taxes",
            "waiver": "₹2 Lakh annual spend",
            "key_benefit": "Automatic statement credit of cashback",
            "category": "Cashback",
            "source": "https://www.paisabazaar.com",
            "points_system": {
                "unit": "Cashback Point",
                "cash_conversion": "1 Point = ₹1.00 (Automatic Statement Credit)",
                "flight_conversion": "N/A (Direct Cashback Card)",
                "hotel_conversion": "N/A (Direct Cashback Card)",
                "redemption_portal": "Automatic",
                "where_to_use": "Credited directly to your card statement within 2 days of statement generation."
            }
        },
        {
            "name": "Axis Bank Ace Credit Card",
            "best_for": "Bill Payments, Daily Use",
            "rewards": "5% on GPay bills",
            "lounge": "8 visits/year (Domestic)",
            "joining_fee": "₹499 + GST",
            "annual_fee": "₹499 + GST",
            "waiver": "₹2 Lakh annual spend",
            "key_benefit": "Industry-best cashback on utility bills",
            "category": "Cashback",
            "source": "https://www.cardmaven.in",
            "points_system": {
                "unit": "Cashback",
                "cash_conversion": "Direct Cashback (1:1 value)",
                "flight_conversion": "N/A",
                "hotel_conversion": "N/A",
                "redemption_portal": "Automatic",
                "where_to_use": "Automatically credited to your next month's statement."
            }
        },
        {
            "name": "Amex Platinum Travel Credit Card",
            "best_for": "Travel",
            "rewards": "Up to 8% milestone rewards",
            "lounge": "2 visits/quarter (Domestic)",
            "joining_fee": "₹3,500 + GST",
            "annual_fee": "₹5,000 + GST",
            "waiver": "None",
            "key_benefit": "Taj Vouchers and air miles transfer",
            "category": "Travel",
            "source": "https://www.americanexpress.com",
            "points_system": {
                "unit": "Membership Rewards (MR) Point",
                "cash_conversion": "1 MR = ₹0.25 to ₹0.30 (Statement Credit/Pay with Points)",
                "flight_conversion": "2 MR = 1 Mile (Singapore Airlines, British Airways, Emirates, etc.)",
                "hotel_conversion": "1 MR = 1 Point (Marriott Bonvoy) | 1 MR = 2 Points (Hilton) | 1 MR = 3 Points (Radisson)",
                "redemption_portal": "Amex Rewards Portal",
                "where_to_use": "Best value when transferred to Marriott Bonvoy or used for Gold Collection vouchers (18k/24k points)."
            }
        },
        {
            "name": "Amazon Pay ICICI Credit Card",
            "best_for": "Amazon Shopping",
            "rewards": "5% for Prime Members",
            "lounge": "N/A",
            "joining_fee": "₹0",
            "annual_fee": "₹0",
            "waiver": "Lifetime Free",
            "key_benefit": "No joining or annual fees ever",
            "category": "Shopping",
            "source": "https://www.icicibank.com",
            "points_system": {
                "unit": "Amazon Pay Balance",
                "cash_conversion": "1 Point = ₹1.00 (Amazon Pay Balance)",
                "flight_conversion": "N/A (Can use Pay balance on Amazon Flights)",
                "hotel_conversion": "N/A",
                "redemption_portal": "Amazon.in",
                "where_to_use": "Used as Amazon Pay balance for shopping on Amazon or 100+ partner merchants."
            }
        },
        {
            "name": "HDFC Regalia Gold Credit Card",
            "best_for": "Travel & Lifestyle",
            "rewards": "1.3% to 13.3%",
            "lounge": "12 Domestic, 6 International",
            "joining_fee": "₹2,500 + GST",
            "annual_fee": "₹2,500 + GST",
            "waiver": "₹3 Lakh annual spend",
            "key_benefit": "SmartBuy travel bookings",
            "category": "Premium",
            "source": "https://www.cardmaven.in",
            "points_system": {
                "unit": "Reward Point (RP)",
                "cash_conversion": "1 RP = ₹0.20 (Statement Credit) | 1 RP = ₹0.50 (SmartBuy Flights/Hotels)",
                "flight_conversion": "1 RP = 0.5 Mile (Air India, Vistara, etc.)",
                "hotel_conversion": "2 RP = 1 Point (Accor ALL)",
                "redemption_portal": "HDFC SmartBuy / NetBanking",
                "where_to_use": "Best utilized for flights/hotels via SmartBuy or Gold Catalogue vouchers."
            }
        },
        {
            "name": "Axis Bank Atlas Credit Card",
            "best_for": "Travel, Air Miles",
            "rewards": "1% to 10%",
            "lounge": "8 Domestic, 4 International",
            "joining_fee": "₹5,000 + GST",
            "annual_fee": "₹5,000 + GST",
            "waiver": "None",
            "key_benefit": "Unmatched air miles value",
            "category": "Travel",
            "source": "https://www.axisbank.com",
            "points_system": {
                "unit": "EDGE Mile",
                "cash_conversion": "Not recommended (Low value)",
                "flight_conversion": "1 EDGE Mile = 2 Partner Points (Most Airlines) | 1 EDGE Mile = 1 Partner Point (Marriott)",
                "hotel_conversion": "1 EDGE Mile = 2 Partner Points (Most Hotels)",
                "redemption_portal": "Axis Travel EDGE Portal",
                "where_to_use": "Unbeatable for transfer to airline partners like Singapore Airlines, Qatar Airways, etc."
            }
        },
        {
            "name": "Tata Neu Infinity HDFC Bank",
            "best_for": "UPI, Tata Neu Spends",
            "rewards": "1.5% to 5%",
            "lounge": "8 Domestic, 4 International",
            "joining_fee": "₹1,499 + GST",
            "annual_fee": "₹1,499 + GST",
            "waiver": "₹3 Lakh annual spend",
            "key_benefit": "Rewards on UPI spends via Tata Neu",
            "category": "Lifestyle",
            "source": "https://www.taneu.com",
            "points_system": {
                "unit": "NeuCoin",
                "cash_conversion": "1 NeuCoin = ₹1.00",
                "flight_conversion": "1 NeuCoin = 1 Air India Point (Usually)",
                "hotel_conversion": "1 NeuCoin = ₹1.00 at IHCL Hotels",
                "redemption_portal": "Tata Neu App",
                "where_to_use": "Redeem at Tata Brands (BigBasket, 1mg, Croma, Air India, IHCL) via Tata Neu app."
            }
        },
        {
            "name": "OneCard (Metal)",
            "best_for": "Students, First-time users",
            "rewards": "1% to 10% (Around You offers)",
            "lounge": "N/A",
            "joining_fee": "₹0 (FD based for students)",
            "annual_fee": "₹0 (Lifetime Free)",
            "waiver": "N/A",
            "key_benefit": "Cool metal card, instant virtual card, easy FD-based limit",
            "category": "Student",
            "source": "https://getonecard.app",
            "points_system": {
                "unit": "Reward Point",
                "cash_conversion": "10 Points = ₹1.00 (Statement Credit)",
                "flight_conversion": "N/A",
                "hotel_conversion": "N/A",
                "redemption_portal": "OneCard App",
                "where_to_use": "Directly redeem points against any transaction in the app (Fractional redemption allowed)."
            }
        },
        {
            "name": "Scapia Federal Credit Card",
            "best_for": "Students, Young Travelers",
            "rewards": "10% Scapia Coins on travel",
            "lounge": "Unlimited Domestic (on ₹5k monthly spend)",
            "joining_fee": "₹0",
            "annual_fee": "₹0 (Lifetime Free)",
            "waiver": "N/A",
            "key_benefit": "Zero Forex Markup, Unlimited Lounge access",
            "category": "Travel",
            "source": "https://www.scapia.cards",
            "points_system": {
                "unit": "Scapia Coin",
                "cash_conversion": "5 Coins = ₹1.00 (Only for Travel bookings)",
                "flight_conversion": "1:5 value for flights via Scapia App",
                "hotel_conversion": "1:5 value for hotels via Scapia App",
                "redemption_portal": "Scapia App",
                "where_to_use": "Used exclusively for booking flights and hotels within the Scapia app."
            }
        },
        {
            "name": "slice Card",
            "best_for": "Lifestyle, Instant Rewards",
            "rewards": "Up to 2% cashback",
            "lounge": "N/A",
            "joining_fee": "₹0",
            "annual_fee": "₹0",
            "waiver": "N/A",
            "key_benefit": "Instant 'spark' offers, great UI/UX, transparent tracking",
            "category": "Student",
            "source": "https://www.sliceit.com",
            "points_system": {
                "unit": "Monies",
                "cash_conversion": "1 Monie = ₹1.00 (Statement Credit)",
                "flight_conversion": "N/A",
                "hotel_conversion": "N/A",
                "redemption_portal": "slice App",
                "where_to_use": "Convert Monies to cash and use it to pay your bill or buy vouchers."
            }
        }
    ]
    return jsonify(cards_data)
