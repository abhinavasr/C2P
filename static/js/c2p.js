
// Define parameters for initializing Mastercard Checkout Services
const srcDPAID = "e1069096-8087-406e-a96a-db3c85ce57da_dpa1"
var params = {
    srcDpaId: srcDPAID, // Unique DPA Identifier, generated during registration.
dpaData: {
        dpaName: "Abhi's Page"   // Name of the Data Protection Agreement (DPA)
},
dpaTransactionOptions: {
        dpaLocale: "en_US",  // Locale for DPA transactions
},
    cardBrands: ["mastercard"]  // List of supported card brands
};


var mcCheckoutService = new MastercardCheckoutServices()
var selectedSRCCardId = null; // Store the selected SRC Card ID here

function authenticationComplete (payload) {
    
    var srcCardList = document.getElementById("srcCardList")
    srcCardList.style.display = "block";
    document.getElementById('src-otp-input').style.display = "none";
    
    srcCardList.loadCards(payload);
    srcCardList.addEventListener('selectSrcDigitalCardId', function (event) {
        console.log('srcDigitalCardId: ', event.detail);
        // handle selected card
        selectedSRCCardId = event.detail;
    });
}

function authenticationFailed (payload) {
    // handle error
    // document.getElementById('src -otp-input').errorReason = "CODE_INVALID";

}



async function initializeMastercardCheckoutServices() {
try {
        var result = await mcCheckoutService.init(params)     
        // handle result: an object containing a list of initialized card networks
        // upon successful resolution, other methods, e.g. getCards(), may be called
        var cards =  await mcCheckoutService.getCards()

        if (cards.length > 0){
            // document.getElementById("srcCardList").style.display = "block";
            authenticationComplete(cards)
        }
        else {
            document.getElementById("srcCardList").style.display = "none";
            var userEmail = document.querySelector('.user-email').innerText;
            // populate the data in { "email" : "test@user.com" } format
            var sampleiDLookupParams = {email: userEmail }
            try{
                var idLookupResult = await mcCheckoutService.idLookup(sampleiDLookupParams) 
                if(idLookupResult){
                    // display authIframe
                    // document.getElementById("authIframe").style.display = "block";

                    try{
                        validationChannel = await mcCheckoutService.initiateValidation() 
                        // handle validation channel result
                        console.log("validationChannel", validationChannel)
                        // make the OTP page visiblie src-otp-input
                        const srcOtpInput = document.querySelector('src-otp-input');
                        srcOtpInput.style.display = "block";
                        // convert this to function <src-otp-input masked-identity-value="+1 (***) ***-*949"></src-otp-input>
                        
                        // srcOtpInput.masked-identity-value = validationChannel.maskedIdentityValue;
                        srcOtpInput.loadSupportedValidationChannels(validationChannel.supportedValidationChannels)
                        
                        srcOtpInput.addEventListener('resendOtp', function(e) {
                            console.log(e.detail, 'OTP resend requested by user');
                        });
                        srcOtpInput.addEventListener('notYouRequested', function () {
                            console.log('user requested Not you? method');
                        });

                        document.querySelector('src-otp-input').addEventListener('otpChanged', function ({ detail }) {
                            console.log('user changed OTP:', detail);
                            if(detail.length>5){
                                otpval = {value: detail}
                                validateOtp = mcCheckoutService.validate(otpval)
                                validateOtp.then(authenticationComplete).catch(authenticationFailed)
                            }
                        })

                    }catch (error){
                        console.log(error);
                    }
                }
            } catch (error){
                console.log(error);
            }
            

        }
    }
    catch (error) {
    console.log(error);
    }
}

initializeMastercardCheckoutServices()

async function makePayment(){

    if(selectedSRCCardId!= null){

        var TransactionAmount = 
        {            
            // DPA-specific preferences and transaction configuration parameters.
            transactionCurrencyCode: "USD",
            transactionAmount: total,            
        }

        var PaymentOptions= [
            {
                dynamicDataType: "CARD_APPLICATION_CRYPTOGRAM_SHORT_FORM"
            },
        ];

        var AuthenticationPreferences = {
            // DPA-specific preferences and transaction configuration parameters.
            payloadRequested : "AUTHENTICATED",
            
        }

        

        var DpaTransactionOptions = {
            // DPA-specific preferences and transaction configuration parameters.
            // See https://developer.mastercard.com/checkout/documentation/api/dpa-transaction-options/ for more details.
            transactionAmount: TransactionAmount,
            dpaBillingPreference: 'NONE',
            dpaLocale: 'en_US',
            merchantCountryCode: "US",
            authenticationPreferences: AuthenticationPreferences,
            paymentOptions: PaymentOptions , // optional
            // threeDsPreference: "NONE",
            merchantCategoryCode: "0001",
            acquirerBIN: "545301", // optional
            acquirerMerchantId: "SRC3DS", // optional
        }

        //launch a pop-up and wait for response

        const popup = window.open('', 'customPopup');

        if (popup) {
            var params = {
                windowRef: popup, // required.
                srcDigitalCardId: selectedSRCCardId, // optional.
                dpaTransactionOptions: DpaTransactionOptions, // optional.
                rememberMe: "true", // optional.
                // DPA-specific preferences and transaction configuration parameters.
            }

            try{
                // Create a payment request object
                checkoutwithcard = await window.mcCheckoutService.checkoutWithCard(params)
                console.log(checkoutwithcard)
                popup.close()

                if(checkoutwithcard.checkoutActionCode == "COMPLETE"){
                    // The checkout was successful, and the payment has been authorized.
                    // You can now complete the transaction by submitting it to your server for settlement.
                    // JS function to call post method with data checkoutwithcard.checkoutActionCode
                    data = {
                        dpaTransactionOptions : {transactionAmount: {transactionAmount: total,transactionCurrencyCode: "USD"}},
                        srcDpaId: srcDPAID, //required
                        correlationId: checkoutwithcard.correlationId, // required.
                        checkoutType: "CLICK_TO_PAY",
                        checkoutReference:{
                            type: "MERCHANT_TRANSACTION_ID",
                            data: {
                                merchantTransactionId: checkoutwithcard.headers['merchant-transaction-id']
                            }
                        }
                    }

                    const response = await fetch('/checkoutAPI', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                        });
                    
                    openSuccessModal();
                    console.log("Payment Successful");
                }

            } catch (error){
                console.log(error);
            }
        }

        
    }
}
