A Simple Workflow for Building CloudFormation Templates
Posted by J Cole Morrison on August 23rd, 2019.

A Simple Workflow for Building CloudFormation Templates

So you've decided to learn CloudFormation! Or maybe your company decided it for you. Either way, unless you're an AWS veteran, stoic sage, or on something strong, you're likely feeling a bit overwhelmed. Seeing some of those long winding JSON or YAML templates span thousands of lines long...well...where do you even start? And when you compound that on top of all of the services that you can work with, the hidden parts beneath those services, and the nuances of the CloudFormation template syntax...it can be a bit much to take in.

However, it's not so bad. Like all tools and technologies with 1000s of bells and whistles, CloudFormation templates have general patterns that, once you pick up on, make creating anything with them exceptionally easier. The one we're going to go over today is a simple workflow to build any service in AWS using CloudFormation templates that will keep you from getting lost in the dark depths of documentation.

"What? You lie."

No, this isn't a lie, but at the same time, we need to clarify a very common misunderstanding that pops up when folks first start using CloudFormation:
CloudFormation is not a shortcut for learning AWS Services

In fact, it assumes that you KNOW the service you're looking to build with very well. That's why any given documentation page in the CloudFormation resource reference is relatively sparse. Though I suppose that could also be from neglect from whatever team deals with writing the documentation.

I bring this up, because marketing teams around these services are very good at building up these tools as if they're the savior of our times, capable of ending developer ideology wars fought in the recesses of forums comments, bringing peace between teams, and probably solving world hunger. Proof? Somehow packaged, one-off containers that run code on a server have been accepted as "serverless."

Anyhow, my point is that CloudFormation is not the first step. It's the step AFTER you know a service already. However, the best place to pick up this understanding is NOT in CloudFormation. If you don't know the service and you try to begin in CloudFormation, well...good luck, have fun. But you probably won't have fun, and if you're like me, luck will ensure that you're up far later than you intended to be fuming over esoteric errors.
Okay, So What's this Workflow?

We'll walk through a simple example shortly, but here's the workflow you should take if you want to effectively build out something in CloudFormation:

    Learn and build the service of interest in the Console
    Using the Console flow as a guideline, build the CloudFormation Template

"Cole this sounds like extra work and/or a pointless step."

Nope! In fact, flying blind without any type of guardrails to direct your labor is a pointless step. Now, before you brush this off, let's see a practice example using EC2 since most folks are pretty familiar with it. So, I'm going to assume you've got step one down and know EC2. You've created EC2 instances, played around with them, etc. You don't need to be a master, but you shouldn't be phased by setting one up.

(If you're not familiar with EC2, you can check out a free EC2 Fundamentals Series here.)
An Example Scenario

So let's say that you want to go and build a CloudFormation template that launches a simple EC2 instance. What's the first move? Well, I'd say most folks would go straight to the AWS::EC2::Instance documentation and start sifting through the myriad of properties. Probably in alphabetical order. Then, the most common step two is looking at the examples and inevitably copy and pasting.

Sure, this will work for simpler one-off things, but the moment you need to create something more complex that connect many different resources...this workflow will create even more overwhelm. That being said, because we don't want this post to turn into an odyssey, we'll still stick with EC2 instances. Therefore, forget these past two paragraphs, I mainly put them here to lay out the scenario and point out the usual way of things.
An Example of the Workflow
First, Build it in the Console

Let's dig into the thought process here. If I wanted to build an EC2 instance in the console, what would we need to do?

    Head over to the AWS Console

    Go to the EC2 console

    Select Instances from the EC2 Console

    Click "Launch Instance"

    Select an AMI type

    Select an Instance Type

    Fill in any Instance Details

    Connect any additional storage volumes

    Add any tags

    Configure / select security groups

    Review, select an EC2 key pair, and launch

Nice. Alright, and how does this help us build the template? Because we can use this pattern above to build out the instance itself.
Second, Using the Console Flow as a Guideline, Build it in CloudFormation

    Head to the CloudFormation Template Resource and Property Types Reference and "pretend" it's the Console.

    Select EC2 from the list of links.

    Select AWS::EC2::Instance from the resource types.

    Code the basic properties:

    {
      "Resources": {
        "ExampleInstance": {
          "Type" : "AWS::EC2::Instance",
          "Properties" : {
          }
        }
      }
    }

    Code in the AMI type

    {
      "Resources": {
        "ExampleInstance": {
          "Type" : "AWS::EC2::Instance",
          "Properties" : {
            "ImageId": "ami-0b898040803850657"
          }
        }
      }
    }

    Code in the Instance Type

    {
      "Resources": {
        "ExampleInstance": {
          "Type" : "AWS::EC2::Instance",
          "Properties" : {
            "ImageId": "ami-0b898040803850657",
            "InstanceType": "t2.micro"
          }
        }
      }
    }

    Fill in any instance details

    {
      "Resources": {
        "ExampleInstance": {
          "Type" : "AWS::EC2::Instance",
          "Properties" : {
            "ImageId": "ami-0b898040803850657",
            "InstanceType": "t2.micro",
            "Tenancy": "default",
            "SubnetId": "subnet-1234567890abcdefg"
          }
        }
      }
    }

    We'll leave additional storage volumes alone so that we can focus on our workflow here.

    Code in any tags

    {
      "Resources": {
        "ExampleInstance": {
          "Type" : "AWS::EC2::Instance",
          "Properties" : {
            "ImageId": "ami-0b898040803850657",
            "InstanceType": "t2.micro",
            "Tenancy": "default",
            "SubnetId": "subnet-1234567890abcdefg",
            "Tags": [{ "Key": "Name", "Value": "Example Instance" }]
          }
        }
      }
    }

    Code in any security groups

    {
      "Resources": {
        "ExampleInstance": {
          "Type" : "AWS::EC2::Instance",
          "Properties" : {
            "ImageId": "ami-0b898040803850657",
            "InstanceType": "t2.micro",
            "Tenancy": "default",
            "SubnetId": "subnet-1234567890abcdefg",
            "Tags": [{ "Key": "Name", "Value": "Example Instance" }],
            "SecurityGroupIds": ["sg-1234567890abcdefg"],
          }
        }
      }
    }

    Review it, and code in your EC2 Key Pair

    {
      "Resources": {
        "ExampleInstance": {
          "Type" : "AWS::EC2::Instance",
          "Properties" : {
            "ImageId": "ami-0b898040803850657",
            "InstanceType": "t2.micro",
            "Tenancy": "default",
            "SubnetId": "subnet-1234567890abcdefg",
            "Tags": [{ "Key": "Name", "Value": "Example Instance" }],
            "SecurityGroupIds": ["sg-1234567890abcdefg"],
            "KeyName": "example-key-pair"
          }
        }
      }
    }

Hopefully you see what we just did there. We used the steps we'd take in the console, to create an EC2 instance, as a one-to-one framework for building out the instance in CloudFormation. By "pretending" that the CloudFormation Resource and Property Types Reference is the AWS console we can skip the overwhelm of where to go and what to do. Finally, we used the console's process of creating an instance to outline which properties we absolutely needed and in what order to code them in.

Doing it like this saves a ton of time that otherwise goes to indecision and finagling around with organization and starting points for development. It lets your brain associate a VISUAL with what you're doing in the code, which makes it far more understandable. It also lets you focus on the ESSENTIAL properties of whatever resource you're creating, instead of getting wrapped up on various options that exist for special cases. Considering that CloudFormation templates can be tens of thousands of lines long, any type of support we can get is highly welcomed.
But Remember, Learn the Service First

Now, this wraps us back around to the first point in this mental workflow: Learn the service and build the service in the Console FIRST. Why? Well, why do we make prototypes? Why do we start application designs on pen and paper or in other sketch tools? Because the feedback loop is much shorter. If we want to see how something looks a bit to the right, well it's as simple as dragging the element over, or redrawing it if you're doing it by hand. However, trying to prototype with code is a MUCH longer feedback loop since moving an element around or changing colors is going to take more effort and time.

Well, similarly, if you're looking to learn a new service, you don't really want to dive right into the deep end. The CloudFormation documentation isn't nearly as clear or as helpful as the console. As much as we developers would love to operate on rote lists of text, it's far FASTER to start somewhere that let's us focus on the concepts of whatever it is we're trying to build. Need to play around with a setting? Okay, tweak it with a few buttons. Otherwise you'll be tweaking it in the code, waiting for CloudFormation to launch template's resources, and hoping you don't get a nasty rollback that takes 5 to 10 minutes...only to do it again.
The Workflow in a Nutshell

So, one more time on the simple workflow for building CloudFormation Templates:

    Learn and build the service of interest in the Console
    Using the Console flow as a guideline, build the CloudFormation Template

Really though, #2 could be reworded as "just pretend the CloudFormation Resource and Property Types Reference is the console." Because that alone will give your mind a lot of direction when navigating its depths.

Yes, I know the example was simple. No, this isn't a panacea. But YES, the time savings you'll get that otherwise go to indecision, organization, and long feedback loops is invaluable.

