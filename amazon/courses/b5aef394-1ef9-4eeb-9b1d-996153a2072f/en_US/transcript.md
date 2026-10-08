[Home](../../../README.en.md) · [Topic guide](../../../LEARNING_GUIDE.md#fulfillment-and-shipping) · [All courses](../../../课程目录.md) · [中文](../zh_CN/transcript.md)

> Compiled and maintained by [SHIN](https://github.com/haloshin) · [Original repository and updates](https://github.com/haloshin/seller-university) · [Attribution and use](../../../../NOTICE.md)
> Course source: Amazon Seller University. Please retain the source and editorial credit; do not claim SHIN's work as your own or imply official endorsement.

# Multi-Channel Fulfillment: Create fulfillment orders

Welcome to our training on how to create multi-channel fulfillment or MCF orders. MCF allows businesses to use Amazon's storage and fulfillment solutions for orders placed on their own website or other e-commerce channels.
 In this video, we'll show you how to create and manage MCF orders in Seller Central. When your customer makes a purchase, you'll create an MCF order.
 This signals Amazon to pick, pack, and ship your customer's order. You can create fulfillment orders in one of three ways.
 Place a single order to create orders one at a time, place orders in bulk via a spreadsheet, or create an automatic order through pre-built integrations or APIs.
 To create orders one at a time, navigate to sellercentral.amazon.com/GC/MCF, then select Place Single Order.
 You can also open the main menu in Seller Central, hover over Orders, and select Create MCF Order.
 This is where you'll provide your order details. We'll prompt you to enter your customer's shipping information.
 Remember to select Add a line to enter more details, like an apartment or floor number, for example.
 We also recommend adding the customer's phone number or email address, so we can send them a shipping notification with tracking details.
 Next, you'll add items to the order. Search by a product's title, MSKU, ASIN, or FNSKU, then let us know how many units of each product we should send to your customer.
 Complete the additional fields if you'd like to customize your order ID or the packing slip's date and comments.
 Before moving on to the next section, it's important to note that we'll ship your eligible orders in unbranded packaging at no additional cost.
 We'll always default to unbranded packaging for MCF orders unless doing so results in longer shipping and delivery times.
 Select the only ship with blank boxes toggle if you'd like to ensure your eligible orders are shipped in unbranded packaging.
 Refer to the FAQs section on the Multi-Channel Fulfillment page for more information on the categories, sizes, and weights that make a product ineligible for unbranded packaging.
 Finally, you'll choose your shipping speed and estimated time of arrival as well as shipment cost.
 After you've double checked each section of your order form, click Place Order.
 The order will ship within two business days if you selected standard shipping speed or the next business day if you selected expedited or priority speeds.
 You can choose to create a hold order instead of placing a fulfillment order.
 This option lets you reserve the ordered items for this customer.
 When you're ready to initiate the shipment for an existing hold order, open the main menu in Seller Central, hover over Orders and select Manage Orders.
 Enter the MCF Order ID to find it listed.
 Then click the Order ID link in the Order Details column and click Ship this order on the MCF Order Details page.
 Note that we'll automatically cancel an order if it isn't activated within 14 days.
 Now let's review how to place a bulk MCF order.
 This method is ideal for large volume orders since bulk orders allow you to use a spreadsheet to upload multiple MCF orders simultaneously.
 From the Place a Multi-Channel Fulfillment Order page, you can either select Create a Bulk Order or you can return to the main page for MCF and click Place Bulk Order.
 From the Multi-Channel Fulfillment Bulk Orders page, you'll select the Create Order tab.
 Then select Download Create Order Template and open the file.
 Click the Instructions tab and read through each step before you begin adding any information to the spreadsheet.
 The fifth step instructs you to review the Example tab to help you avoid including invalid information with your fulfillment request.
 Let's review one example together. You can reference the chapters listed in the description of this video if you'd like to skip ahead.
 First, note any bolded words in the first row of the spreadsheet.
 These represent required fields while the others are optional.
 In this training, we'll provide examples of the required fields.
 Start by entering your order information. In Columns A and B, you'll enter a unique identifier for your order ID using between 1 and 40 characters.
 Make sure you only include numbers or letters or a combination of the two.
 We recommend you use the same value for both Columns A and Columns B.
 In this example, a customer placed an order for three different SKUs. Give each SKU its own row, but only use one order ID for the entire order.
 Note that Merchant SKU, Quantity, and Merchant Fulfilled Order Item ID are the only columns you'll need to complete for each SKU in the same order.
 Otherwise, the items you include in the order's first row will apply to all other items in the order.
 Next, you'll add the order date in Column C. This is the date that will show on the order's packing slip.
 Here's how you'll format it. Use four digits for the year, two digits for the month, and two digits for the day, and separate each with a dash.
 For example, 2022-11-01. Add the letter T directly after the day, which will separate the date and time of the order.
 To add the order's time, use two digits for the hour, two digits for the minute, and two digits for the second, separating each with a colon.
 For example, you'd input 21 colon 32 colon 52 if the order was placed at 52 seconds past 9:32 pm.
 Check that your order date doesn't include spaces, and take a close look at the Data Definitions tab to make sure you understand how to format your date before proceeding.
 In Column D, enter the unique product identifier assigned by the merchant. Make sure it's between 1 and 40 alpha numeric characters.
 Note that the SKU must be unique for each product.
 Use Column E to add the amount of items Amazon will need to ship in the order, and use Column F to add a unique identifier for each item.
 Make sure the identifier is between 1 and 90 alpha numeric characters. We'll add the text you enter in Column J to the order's packing slip.
 We recommend you include information like your company's website, return policy, or contact information.
 Put the delivery service level in Column K. You can enter one of three options, standard, express, or priority.
 Standard is three to five business days, while express is two business days, and priority is one business day.
 Enter your customer's name and delivery address in Columns L through S.
 Reference the Data Definitions tab to ensure you've formatted them correctly, and remember to use a two-digit country code in Column Q and a two-digit state or region code in Column R.
 After you've reviewed the instructions, data definitions, and example tabs, click the Fulfilment Request tab and enter your orders.
 Then save your file in a tab delimited.txt file format. Return to the Multi-Channel Fulfilment Bulk Orders page in Seller Central to upload your spreadsheet.
 Click Upload Template, choose the file, and select Submit File. Click Refresh to view your upload's progress.
 After it's completed, you can review the generated report for errors and warnings.
 We'll only create error-free orders, so be sure to correct and resubmit those with errors.
 A third way to place an MCF order is via APIs.
 These integrations connect to your sales channels to automate MCF order creation.
 This option doesn't require coding and links you to popular e-commerce websites, like Shopify and WooCommerce.
 You can also create your own custom API by referencing our developer documentation.
 Visit supplychain.amazon.com/integrations to read our guide on e-commerce integrations, or you can download developer documentation for more information.
 You can check the status of an MCF order on the Manage Orders page in Seller Central or via API reporting.
 To access the Manage Orders page, open the Seller Central main menu, hover over Orders, and click Manage Orders.
 Remember to click View FBA Orders, then use the Order ID field to search for your MCF order.
 You can also select the Non-Amazon Sales Channel filter to browse a list of all your MCF orders.
 After you select an order, you can reference the order's details.
 These include shipment information, the order status of each item, whether the order has shipped, and the tracking number associated with the shipment.
 The page will also include a link to the Swiship Tracking website, which provides tracking information for all carriers.
 To search an order, simply enter the tracking number.
 If your order hasn't shipped, the page will display an estimated shipping and delivery date.
 If you'd like to initiate a return for an MCF order, first decide whether you want the customer to ship the items back to Amazon.
 We can add them to your inventory once they're returned, but you're responsible for shipping the items to the Amazon Fulfillment Center and for refunding the customer.
 Here's how you can initiate a return to Amazon.
 Go to the Multi-Channel Fulfillment Order Details page for that order in Seller Central.
 Select the Returns tab and select the items and quantities for return from the Return Quantity drop-down menu.
 Then choose the reason for each item and click Submit Return.
 This submission will generate a return merchandise authorization form, also known as an RMA form, which contains a return mailing label and a return authorization slip.
 Ask your customer to affix the return mailing label to their package before sending it back to Amazon.
 Each label contains the address of the Amazon Fulfillment Center that will receive and process the return.
 Note that postage isn't provided with return labels, so you or the customer are responsible for purchasing postage for the return.
 The return authorization slip is a form that includes a barcode and item description for the products your customer is returning.
 Let your customer know they must include it in the package with the items they're returning.
 After you've initiated a return, you'll see the return status on the same Multi-Channel Fulfillment Order Details page you use to create the return.
 Note that, like with creating a fulfillment order, you can also create a return by using an API.
 You can learn more on our Integrations page.
 Reference the FAQs section on the Multi-Channel Fulfillment page for more information on getting started, shipping and packaging, and returns and reimbursements.
 We also recommend watching the Multi-Channel Fulfillment "How It Works" video in Seller University to learn more about the MCF program and its benefits.
 This concludes our training on how to create and manage fulfillment orders with MCF.
 Thank you and happy selling in the Amazon Store.

---

[Plain text](transcript.txt) · [Captions](captions.vtt)

[Watch this official course](https://sellercentral.amazon.com/su/learn?mons_sel_locale=en_US&learningModuleId=b5aef394-1ef9-4eeb-9b1d-996153a2072f) · Course ID, audio language and archived version matched; availability may change.

[Previous in topic：Multi-Channel Fulfillment (MCF): How Amazon sellers can use MCF and FBA together](../../../courses/9c8d24db-75e1-4d42-b405-796c5bc19cad/en_US/transcript.md) · [Next in topic：Multi-Channel Fulfillment: How it works](../../../courses/fc0c4ad6-1655-4418-be86-bf00c8f7cf16/en_US/transcript.md)
