Quickstart
==========

Assets module consists of 2 different use cases:  - Back Office, and Data Center. 
These are 2 different because of field types, and data sources. Lets start with 
the data center type.

.. image:: overview.png


Searching/Filtering Assets
----------------

Lets start with the main screen. Here you find all your hardware assets added 
to the database. Use left column for filtering for assets. 

Assets consists of 2 types - devices and parts. Device could be Blade Server,
and parts is a component of this server, eg. Memory or Hard Drive. One part can
be assigned to one device at the time. You can move parts from one device to
another when you need it.

.. image:: actions.png

You can use Actions menu to trigger actions on selected device/part.

Adding Assets
-------------

Now, lets add some devices and parts. Click Add device from top menu 

.. image:: add-devices.png

- Type - read only field for Data Center, or Back Office / Administration for BO. 
  Administration is used for Assets like Buildings etc.
- Model - type couple of letters to search for given model. If not found in the database, 
  just click 'Add button' to be able to add it.
- Status - asset lifetime indicator. Newly buyed assets has status 'new'. 
  You can change it as required according to your own workflow. 
- Warehouse - the place where asset is located in. 
- Price - unit price for 1 asset.
- Support type - you can specify support details here, such as support conditions.
- Provider - assets provider name.
- Additional remarks - additional info.
- Request date, Provider order date, Delivery date, Invoice date, Production use date - 
  for now you can choose dates as required. Later it will be integrated with 
  the workflow system.
- Size in units - type how many "U" - units will device take

Serial number is mandatory for assets. You can also optionally enter barcodes 
for them as well. 
You can paste serial numbers and barcodes in series, thus allowing you to 
batch-add many devices of the same type. 


Adding Parts
-------------

You can in the same way add parts to the assets databse, and bind the part to 
the device. To do this, choose Menu->Add part.


.. image:: add-parts.png

- When the part is marked as ``salvaged``, you can enter here the old barcode data.
- On this screen barcodes are not visible, because parts doesn't have barcodes assigned. 

Bulk editing
-------------
It is often required to edit multiple Assets at once, when you want for example 
to move it from one warehouse to another. Special mode called 'bulk edit' 
is for this case provided. 

To activate this mode, go to the search screen, and select multiple assets 
using check marks on the left side.

.. image:: bulk-1.png

when ready, choose Edit selected from bulk edit actions. 

.. image:: bulk-2.png

On the next screen you can edit theese records at once changing appropriate 
fields. When filled one field with given value, you can propagate 
this value for all records by clicking on the "plus" mark near current cell.


Workflow / Statues
-------------

.. image:: edit-device-status.png

In this version there are no limits for moving assets from one status to another. 
You can freely change statuses. All changes will be recorded on status changes 
table, allowing you to inspect flow later.

Edit device
-------------

.. image:: edit-device.png

In every case, you can edit assets fields as you like. From this screen you 
can add parts by clicking on the 'Add part' button. 

Admin
-----
Administration interface is accessible from within Menu. 

Here you can define
- models
- categories
- warehouses
- other dictionary data.
