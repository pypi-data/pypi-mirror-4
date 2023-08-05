# Cloud DNS

## Basic Concepts
The Cloud DNS API allows you to programmatically associate domain names with your devices, and add/edit/remove DNS records for those domains.


## About Domain Names
Rackspace does not handle domain name registration. You will have to go to any one of the many existing registrars if you need to register a domain name. Once your domain name is registered, you can then use it with your Rackspace Cloud account.

For the purposes of this document, the domain **example.edu** will be used. This is not a real domain; it is a domain name reserved for use in documentation. See this [Wikipedia](http://en.wikipedia.org/wiki/Example.com) article for more information about the use of this name.

**Subdomains** are domains within the parent domain, and are typically used to designate different functions within the domain. Examples of subdomains would be `mail.example.edu` (for handling email activity), `www.example.edu` (web traffic), and `ftp.example.edu` (FTP traffic). Subdomains can be further broken down into sub-subdomains, such as `main.ftp.example.edu` and `secondary.ftp.example.edu`, to suit the needs of the site.


## Cloud DNS in pyrax
Once you have authenticated and connected to the Cloud DNS service, you can reference the DNS module via `pyrax.cloud_dns`. This module provides methods for managing your DNS entries for the cloud.

All of the code samples in this document assume that you have already imported pyrax, authenticated, and created the name `dns` at the top of the script, like this:

    import pyrax
    pyrax.set_credential_file("my_cred_file")
    # or
    # pyrax.set_credentials("my_username", "my_api_key")
    dns = pyrax.cloud_dns


## Listing Domains
To get a list of all the domains that are manageable by your account, call the `list()` method:

    dns.list()

This will return a list of `CloudDNSDomain` objects, with which you can then interact. It is a flat list: there is no hierarchical nesting of subdomains within their parent domains. Assuming that you have just started, you will get back an empty list. The next step would be to add your domains.


## Adding Domains
To create a domain, you would call the `dns.create()` method, supplying some or all of the following parameters:

Parameter | Description | Required?---- | ---- | ----**name** | The fully-qualified domain name (FQDN) | yes**emailAddress** | The email address of the domain administrator | yes**ttl** | The Time To Live (in seconds) for the domain. Default=3600. Minimum=300. | no**comment** | A brief description of the domain. Maximum length=160 characters | no**subdomains** | One or more dicts that represent subdomains of this new domain. The dicts have the same structure as the main domain, with each of these parameters being keys in the subdomain dicts. Including subdomains in the `create()` command is equivalent to creating them separately, but requires only one API call instead of many. | no**records** | You can optionally add DNS records for the domain, such as `MX`, `A`, and `CNAME`. The records are dicts with the same structure as for the `add_records()` method, and adding them in the `create()` command is equivalent to adding them separately afterward, but requires only one API call. | no

So the simplest form of the call would be:

    dom = dns.create(name="example.edu", emailAddress="sample@example.edu")

You could also add a TTL setting and a comment:

    dom = dns.create(name="example.edu", emailAddress="sample@example.edu",
            ttl=600, comment="Primary domain for this documentation.")

The `create()` command returns an instance of a `CloudDNSDomain` object:

    <CloudDNSDomain accountId=000000, comment=Primary domain for this documentation., created=2012-12-06T20:45:10.000+0000, emailAddress=sample@example.edu, id=3534921, name=example.edu, nameservers=[{u'name': u'dns1.stabletransit.com'}, {u'name': u'dns2.stabletransit.com'}], ttl=600, updated=2012-12-06T20:45:10.000+0000>


## Subdomains
Subdomains are conceptually the same as primary domains, but are a useful way of addressing multiple related devices without requiring each to have its own domain name. You create a subdomain just like creating a primary domain: by calling `dns.create()`, but with the `name` parameter replaced with the **FQDN** (Fully-Qualified Domain Name) of the subdomain.

Subdomains in DNS are managed in separate zone files, so this means that there isn't an explicit linkage between a subdomain and the primary domain. Instead, the relationship is only implied, and is the result of the naming: `a.example.edu` is by definition a subdomain of `example.edu`; likewise, `b.a.example.edu` is a subdomain of `a.example.edu`.


## DNS Records
Records specify information about the domain to which they belong. Rackspace Cloud DNS supports the following record types:

* A
* CNAME
* MX
* AAAA
* NS
* TXT
* SRV
* PTR


## Adding Subdomains
Once we have the primary domain object, we can add subdomains

To illustrate the options available for creating subdomains, consider the following desired result: the creation of the `example.edu` domain, along with 4 subdomains: `north.example.edu`, `west.example.edu`, `southeast.example.edu`, and `southby.southeast.example.edu`. The simplest approach would be to call `create()` for each one separately:

    dom = dns.create(name="example.edu", comment="Primary domain",
            emailAddress="sample@rackspace.edu")    subdom1 = dns.create(name="north.example.edu", comment="1st sample subdomain",            emailAddress="sample@rackspace.edu")    subdom2 = dns.create(name="west.example.edu", comment="2nd sample subdomain",
            emailAddress="sample@rackspace.edu")    subdom3 = dns.create(name="southeast.example.edu",            emailAddress="sample@rackspace.edu")    subdom4 = dns.create(name="southby.southeast.example.edu",            comment="Final sample subdomain", emailAddress="sample@rackspace.edu")

Instead of making 5 separate calls, we can define the subdomain information, and pass that along with the single `create()` call:

    subs = [        {"name" : "north.example.edu",            "comment" : "1st sample subdomain",            "emailAddress" : "sample@rackspace.edu"},        {"name" : "west.example.edu",            "comment" : "2nd sample subdomain",            "emailAddress" : "sample@rackspace.edu"},        {"name" : "southeast.example.edu",            "emailAddress" : "sample@rackspace.edu"},        {"name" : "southby.southeast.example.edu",            "comment" : "Final sample subdomain",            "emailAddress" : "sample@rackspace.edu"}        ]
    dom = dns.create(name="example.edu", comment="Primary domain",
            emailAddress="sample@rackspace.edu", subdomains=subs)

The end result is the same, but the second form only makes one API call, and is thus more efficient overall.


## Adding DNS Records
DNS records are associated with a particular domain, so to add records you call the `add_records()` method of the CloudDNSDomain object for that domain. Alternatively, you can call the module's `add_records()` method, passing in the domain reference as well as the record information.

The record information should be a dict whose keys are the relevant record attributes; which keys are needed depend on the record type. To create multiple records in a single call, pass in a list of these record dicts.

Name | Description | Required--- | --- | ---**type** | Specifies the record type to add. | Yes**name** | Specifies the name for the domain or subdomain. Must be a valid domain name. | Yes**data** | The data field for PTR, A, and AAAA records must be a valid IPv4 or IPv6 IP address | Yes**priority** | Required for MX and SRV records, but forbidden for other record types. If specified, must be an integer from 0 to 65535. | For MX and SRV records only**ttl** | If specified, must be greater than 300. Defaults to the domain TTL if available, or 3600 if no TTL is specified. | No**comment** | If included, its length must be less than or equal to 160 characters. | No


## Updating a Domain
Once you have created a domain, you can modify any of the following attributes:

- Contact email address
- TTL
- Comment

To do that, call the domain's `update()` method, or the `dns.update_domain()` method. Given a `CloudDNSDomain` object 'dom', these two commands are equivalent:

    dom.update(ttl=1200)
    # or
    dns.update_domain(dom, ttl=1200)


## Deleting a Domain
If you have a `CloudDNSDomain` object 'dom' that you want to delete, you can use either the object-level or module-level command to do so:

    dom.delete()
    # or
    dns.delete(dom)


## Import / Export a Domain
If you have a BIND 9 formatted domain configuration file (for an example, see [this page](http://www.centos.org/docs/2/rhl-rg-en-7.2/s1-bind-configuration.html#BIND-EXAMPLE-ZONE-WHOLE) from the CentOS site) that describes the domain and its information, you can import that directly instead of creating the separate commands that would be needed to create and configure the domain from scratch.

    with file("/path/to/bindfile.txt") as bindfile:
        data = bindfile.read()
        dom = dns.import_domain(data)










