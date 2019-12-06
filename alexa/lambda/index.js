const Alexa = require('ask-sdk-core');
const Util = require('./util');
const Common = require('./common');

// The namespace of the custom directive to be sent by this skill
const NAMESPACE = 'Custom.Mindstorms.Gadget';

// The name of the custom directive to be sent this skill
const NAME_CONTROL = 'control';

/* CONSTANTS */
const skillBuilder = Alexa.SkillBuilders.custom();
const imagePath = 'https://raw.githubusercontent.com/sanjayseshan/pixelplotter-alexa/master/alexa/pictures/{A}.png' // {A}.{H}x{W}.png';
const photoPath = 'https://raw.githubusercontent.com/sanjayseshan/pixelplotter-alexa/master/alexa/photos/{A}.jpg' // {A}.{H}x{W}.png';
const backgroundImagePath = 'https://raw.githubusercontent.com/sanjayseshan/pixelplotter-alexa/master/{A}.png' // {A}.{H}x{W}.png';
const data = [
  {
    ImageName: 'Taj Mahal', Abbreviation: 'tajmahal', Location: 'Agra, India', ImageYear: 1653, Description: 'The Taj Mahal is an ivory-white marble Islamic mausoleum on the south bank of the Yamuna river in the Indian city of Agra. It was commissioned in 1632 by the Mughal emperor Shah Jahan to house the tomb of his favourite wife, Mumtaz Mahal; it also houses the tomb of Shah Jahan himself. The tomb is the centrepiece of a 17-hectare complex, which includes a mosque and a guest house.',
  },
  {
    ImageName: 'Statue of Liberty', Abbreviation: 'statueofliberty', Location: 'New York, NY', ImageYear: 1876, Description: 'The Statue of Liberty is a colossal neoclassical sculpture on Liberty Island in New York Harbor in New York, in the United States. The copper statue, a gift from the people of France to the people of the United States, was designed by French sculptor Frédéric Auguste Bartholdi and its metal framework was built by Gustave Eiffel. The statue was dedicated on October 28, 1886.',
  },
  {
    ImageName: 'Gateway Arch', Abbreviation: 'saintlouis', Location: 'St. Louis, MO', ImageYear: 1958, Description: 'The Gateway Arch is a 630-foot monument in St. Louis, Missouri, United States. Clad in stainless steel and built in the form of a weighted catenary arch it is the world\'s tallest arch. Built as a monument to the westward expansion of the United States, the Arch, commonly referred to as "The Gateway to the West", is the centerpiece of Gateway Arch National Park and has become an internationally recognized symbol of St. Louis.',
  },
  {
    ImageName: 'Custom', Abbreviation: 'custom', Location: 'Here', ImageYear: 2019, Description: 'Probably a picture of you. I hope you like it.'
  },
];
const defaultItemToken = 'tajmahal';

const welcomeMessage = 'Welcome to Pixel Plotter!';
const repromptOutput = 'What would you like to print?';

/* INTENT HANDLERS */
const ListTemplateHandler = {
  canHandle(handlerInput) {
    const request = handlerInput.requestEnvelope.request;
    return (
      handlerInput.requestEnvelope.request.type === 'LaunchRequest' ||
      (
        request.type === 'IntentRequest' &&
        (
          request.intent.name === 'HorizontalTemplateIntent' ||
          request.intent.name === 'VerticalTemplateIntent' ||
          request.intent.name === 'AMAZON.StartOverIntent'
        )
      )
    );
  },
handle: async function(handlerInput) {
    const request = handlerInput.requestEnvelope;
    let templateDirection = 'vertical';
    let templateNumber = 1;
    const imgHeight = [88];
    const imgWidth = [88];
    
    // inserted Here
    let { apiEndpoint, apiAccessToken } = handlerInput.requestEnvelope.context.System;
    let apiResponse = await Util.getConnectedEndpoints(apiEndpoint, apiAccessToken);
    if ((apiResponse.endpoints || []).length === 0) {
        // return handlerInput.responseBuilder
        // .speak(`I couldn't find an EV3 Brick connected to this Echo device. Please check to make sure your EV3 Brick is connected, and try again.`)
        // .getResponse();
        Util.putSessionAttribute(handlerInput, 'endpointId', -1);

    } else {
        // Store the gadget endpointId to be used in this skill session
        let endpointId = apiResponse.endpoints[0].endpointId || [];
        Util.putSessionAttribute(handlerInput, 'endpointId', endpointId);
    }

    if (handlerInput.requestEnvelope.intent && handlerInput.requestEnvelope.intent.name === 'HorizontalTemplateIntent') {
      templateDirection = 'horizontal';
      templateNumber = 2;
      imgHeight[0] = 280;
      imgWidth[0] = 372;
    }
    let speechOutput = `This is the main menu. Select the image to print by touch or say the image name.`;

    if (supportsDisplay(handlerInput)) {
      const imagesList = [];
      data.forEach((x) => {
        const image = new Alexa.ImageHelper().withDescription(`${x.Abbreviation}`);
        for (let y = 0; y < imgHeight.length; y += 1) {
          image.addImageInstance(getImageUrl(imgHeight[y], imgWidth[y], x.Abbreviation));
        }
        imagesList.push({
          token: x.Abbreviation,
          textContent: new Alexa.PlainTextContentHelper()
            .withPrimaryText(x.ImageName)
            .withSecondaryText(`Location: ${x.Location}`)
            .getTextContent(),
          image: image.getImage(),
        });
      });
      handlerInput.responseBuilder.addRenderTemplateDirective({
        type: `ListTemplate${templateNumber}`,
        token: 'listToken',
        backButton: 'hidden',
        title: `Welcome to Pix3l Plotter Alexa-edition`,
        listItems: imagesList,
      });
    }

    if (handlerInput.requestEnvelope.request.type === 'LaunchRequest') {
      speechOutput = welcomeMessage + speechOutput;
    }

    return handlerInput.responseBuilder
        .speak(speechOutput)
        .reprompt(repromptOutput)
        .getResponse();
  },
  
};

// Construct and send a custom directive to the connected gadget with
// data from the MoveIntent request.
const PrintIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'PrintIntent';
    },
    handle: function (handlerInput) {
        console.log('Inside PrintHandler');

        const intentName = Alexa.getIntentName(handlerInput.requestEnvelope);
        const speakOutput = `You just triggered ${intentName}`;

        const request = handlerInput.requestEnvelope;
        const picture = Alexa.getSlotValue(request, 'Picture');

        // Get data from session attribute
        const attributesManager = handlerInput.attributesManager;
        const endpointId = attributesManager.getSessionAttributes().endpointId || [];

        if (endpointId === -1) {
            return handlerInput.responseBuilder
            .speak(`I couldn't find an EV3 Brick connected to this Echo device. Please check to make sure your EV3 Brick is connected, and try again.`)
            .getResponse();
        }

        // Construct the directive with the payload containing the move parameters
        const directive = Util.build(endpointId, NAMESPACE, NAME_CONTROL,
            {
                type: 'print',
                picture: picture,
            });


        const speechOutput = (picture === "cancel")
            ?  "Cancelling moon"
            : `${picture} printing`;

        return handlerInput.responseBuilder
            .speak(speechOutput)
            .reprompt("awaiting command")
            .addDirective(directive)
            .getResponse();
    }
};

// Construct and send a custom directive to the connected gadget with data from
// the SetCommandIntent request.
const SetCommandIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'SetCommandIntent';
    },
    handle: function (handlerInput) {

        let command = Alexa.getSlotValue(handlerInput.requestEnvelope, 'Command');
        if (!command) {
            return handlerInput.responseBuilder
                .speak("Can you repeat that?")
                .reprompt("What was that again?").getResponse();
        }

        const attributesManager = handlerInput.attributesManager;
        let endpointId = attributesManager.getSessionAttributes().endpointId || [];
        let speed = attributesManager.getSessionAttributes().speed || "50";

        // Construct the directive with the payload containing the move parameters
        let directive = Util.build(endpointId, NAMESPACE, NAME_CONTROL,
            {
                type: 'command',
                command: command,
                speed: speed
            });

        return handlerInput.responseBuilder
            .speak(`command ${command} activated`)
            .reprompt("awaiting command")
            .addDirective(directive)
            .getResponse();
    }
};


const BodyTemplateHandler = {
  canHandle(handlerInput) {
    const request = handlerInput.requestEnvelope.request;
    return (
      (
        request.type === 'IntentRequest' &&
        request.intent.name === 'BodyTemplateSelectionIntent'
      ) || (request.type === 'Display.ElementSelected')
    );
  },
  handle(handlerInput) {
    const responseBuilder = handlerInput.responseBuilder;
    const request = handlerInput.requestEnvelope.request;
    let selectedImage;
    let speechOutput;

    if (handlerInput.requestEnvelope.request.type === 'Display.ElementSelected') {
      // need to fetch token and then look up item from that
      const selectedToken = handlerInput.requestEnvelope.request.token;
      selectedImage = getItemByAbbreviation(selectedToken);
    } else {
      // must be an intent
      let slotIdValue;
      if (request.intent.slots &&
          request.intent.slots.templateSelection &&
          request.intent.slots.templateSelection.value &&
          request.intent.slots.templateSelection.resolutions &&
          request.intent.slots.templateSelection.resolutions.resolutionsPerAuthority &&
          request.intent.slots.templateSelection.resolutions.resolutionsPerAuthority[0] &&
          request.intent.slots.templateSelection.resolutions.resolutionsPerAuthority[0].values &&
          request.intent.slots.templateSelection.resolutions.resolutionsPerAuthority[0].values[0] &&
          request.intent.slots.templateSelection.resolutions.resolutionsPerAuthority[0].values[0].value &&
          request.intent.slots.templateSelection.resolutions.resolutionsPerAuthority[0].values[0].value.name) {
        slotIdValue = request.intent.slots.templateSelection.resolutions.resolutionsPerAuthority[0].values[0].value.id;
        selectedImage = getItemByAbbreviation(slotIdValue);
      }
    }

    if (!selectedImage) {
      selectedImage = getItemByAbbreviation(defaultItemToken);
    }

    responseBuilder.withStandardCard(
      getCardTitle(selectedImage),
      getTextDescription(selectedImage),
      getSmallImage(selectedImage.Abbreviation),
      getLargeImage(selectedImage.Abbreviation),
    );

    speechOutput = getSpeechDescription(selectedImage);

    if (supportsDisplay(handlerInput)) {
      const image = new Alexa.ImageHelper()
        .addImageInstance(getPhotoUrl(selectedImage.Abbreviation))
        .getImage();

      const title = getCardTitle(selectedImage);
      const bodyTemplate = bodyTemplateChoice(getCardTitle(selectedImage));
      const primaryText = new Alexa.RichTextContentHelper()
        .withPrimaryText(getTextDescription(selectedImage, '<br/>'))
        .getTextContent();
      responseBuilder.addRenderTemplateDirective({
        type: bodyTemplate,
        backButton: 'visible',
        // backgroundImage: bgImage,
        image,
        title,
        textContent: primaryText,
      });
      speechOutput = getSpeechDescription(selectedImage);

    }


    return responseBuilder.speak(speechOutput)
      .reprompt(repromptOutput)
      .getResponse();
  },
};



/* HELPER FUNCTIONS */

function bodyTemplateChoice(pImageName) {
  let templateName;

  switch (pImageName) {
    case 'Taj Mahal':
      templateName = 'BodyTemplate2';
      break;
    case 'Statue of Liberty':
      templateName = 'BodyTemplate2';
      break;
    case 'Gateway Arch':
      templateName = 'BodyTemplate3';
      break;
    case 'Custom':
      templateName = 'BodyTemplate6';
      break;
    case 'Washington':
      templateName = 'BodyTemplate7';
      break;
    default:
      templateName = 'BodyTemplate1';
  }
  return templateName;
}


function getBodyTemplateNumber(templateType) {
  switch (templateType) {
    case 'BodyTemplate1':
      return '1';
    case 'BodyTemplate2':
      return '2';
    case 'BodyTemplate3':
      return '3';
    case 'BodyTemplate6':
      return '6';
    case 'BodyTemplate7':
      return '7';
    default:
      break;
  }
  return 'unknown body template';
}


// returns true if the skill is running on a device with a display (show|spot)
function supportsDisplay(handlerInput) {
  const hasDisplay =
    handlerInput.requestEnvelope.context &&
    handlerInput.requestEnvelope.context.System &&
    handlerInput.requestEnvelope.context.System.device &&
    handlerInput.requestEnvelope.context.System.device.supportedInterfaces &&
    handlerInput.requestEnvelope.context.System.device.supportedInterfaces.Display;
  return hasDisplay;
}

function getCardTitle(item) {
  return item.ImageName;
}

function getSmallImage(imageName) {
  return getImageUrl(400, 720, imageName);
}

function getLargeImage(imageName) {
  return getImageUrl(800, 1200, imageName);
}

function getPhotoUrl(imageName) {
  return photoPath
    .replace('{A}', imageName);
}
function getImageUrl(height, width, imageName) {
  return imagePath.replace('{H}', height)
    .replace('{W}', width)
    .replace('{A}', imageName);
}

function getBackgroundImage(height, width, imageName) {
  return backgroundImagePath.replace('{H}', height)
    .replace('{W}', width)
    .replace('{A}', imageName);
}

function getSpeechDescription(item) {
//   return `${item.ImageName} was built in ${item.ImageYear}.  The ${item.ImageName} is located in ${item.Location}`;
    return item.Description;
}

function formatCasing(key) {
  return key.split(/(?=[A-Z])/).join(' ');
}

function getItemByAbbreviation(abbreviation) {
  const propertyArray = Object.getOwnPropertyNames(data[0]);
  let slotValue;

  for (const property in propertyArray) {
    if (Object.prototype.hasOwnProperty.call(propertyArray, property)) {
      const item = data.filter(x => x[propertyArray[property]]
        .toString().toLowerCase() === abbreviation.toLowerCase());
      if (item.length > 0) {
        return item[0];
      }
    }
  }
  return slotValue;
}

function getTextDescription(item) {
  let text = item.Description + '\n\n';  

//   for (const key in item) {
//     if (key !== 'Abbreviation') {
//         if (Object.prototype.hasOwnProperty.call(item, key)) {
//             text += `${formatCasing(key)}: ${item[key]}\n`;
//         }   
//     }
//   }
  return text;
}

/* LAMBDA SETUP */
exports.handler = skillBuilder
  .addRequestHandlers(
    ListTemplateHandler,
    BodyTemplateHandler,
    PrintIntentHandler,
    Common.HelpIntentHandler,
    Common.ExitHandler,
    Common.SessionEndedRequestHandler,
    Common.IntentReflectorHandler, // make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
  )
  .addRequestInterceptors(Common.RequestInterceptor)
  .addErrorHandlers(
    Common.ErrorHandler,
   )
  .withCustomUserAgent('cookbook/display-directive/v1')
  .lambda();
